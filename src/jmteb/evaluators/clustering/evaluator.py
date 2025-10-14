from __future__ import annotations

from os import PathLike
from pathlib import Path
from typing import Callable

import numpy as np
from loguru import logger
from sklearn.base import ClusterMixin
from sklearn.cluster import (
    AgglomerativeClustering,
    Birch,
    BisectingKMeans,
    MiniBatchKMeans,
)
from sklearn.metrics import homogeneity_completeness_v_measure

from jmteb.embedders.base import TextEmbedder
from jmteb.evaluators.base import EmbeddingEvaluator, EvaluationResults

from .data import ClusteringDataset, ClusteringPrediction


class ClusteringEvaluator(EmbeddingEvaluator):
    """
    ClusteringEvaluator is a class for evaluating clustering models.

    Args:
        val_dataset (ClusteringDataset): validation dataset
        test_dataset (ClusteringDataset): evaluation dataset
        prefix (str | None): prefix for sentences. Defaults to None.
        random_seed (int | None): random seed used in clustering models. Defaults to None.
        log_predictions (bool): whether to log predictions of each datapoint.
        encode_kwargs (dict): kwargs passed to embedder's encode function. Defaults to {}.
    """

    def __init__(
        self,
        val_dataset: ClusteringDataset,
        test_dataset: ClusteringDataset,
        prefix: str | None = None,
        random_seed: int | list[int] | None = None,
        log_predictions: bool = False,
        encode_kwargs: dict = {},
    ) -> None:
        self.val_dataset = val_dataset
        self.test_dataset = test_dataset
        self.prefix = prefix
        self.random_seed = random_seed
        self.log_predictions = log_predictions
        self.encode_kwargs = encode_kwargs
        self.main_metric = "v_measure_score"

    def __call__(
        self, model: TextEmbedder, cache_dir: str | PathLike[str] | None = None, overwrite_cache: bool = False
    ) -> EvaluationResults:
        if cache_dir is not None:
            Path(cache_dir).mkdir(parents=True, exist_ok=True)

        logger.info("Converting validation data to embeddings...")
        val_embeddings = model.batch_encode_with_cache(
            [item.text for item in self.val_dataset],
            prefix=self.prefix,
            cache_path=Path(cache_dir) / "val_embeddings.bin" if cache_dir is not None else None,
            overwrite_cache=overwrite_cache,
            **self.encode_kwargs,
        )
        val_labels = [item.label for item in self.val_dataset]

        logger.info("Converting test data to embeddings...")
        if self.val_dataset == self.test_dataset:
            test_embeddings = val_embeddings
            test_labels = val_labels
        else:
            test_embeddings = model.batch_encode_with_cache(
                [item.text for item in self.test_dataset],
                prefix=self.prefix,
                cache_path=Path(cache_dir) / "test_embeddings.bin" if cache_dir is not None else None,
                overwrite_cache=overwrite_cache,
                **self.encode_kwargs,
            )
            test_labels = [item.label for item in self.test_dataset]

        n_clusters = len(set(test_labels))

        logger.info("Fitting clustering model...")
        val_results = {}
        median_seeds = {}

        random_model_constructors: dict[str, Callable[[int | None], ClusterMixin]] = {
            "MiniBatchKMeans": lambda seed: MiniBatchKMeans(n_clusters=n_clusters, n_init="auto", random_state=seed),
            "BisectingKMeans": lambda seed: BisectingKMeans(n_clusters=n_clusters, random_state=seed),
        }
        no_random_model_constructors: dict[str, Callable[[None], ClusterMixin]] = {
            "AgglomerativeClustering": lambda seed: AgglomerativeClustering(n_clusters=n_clusters),
            "Birch": lambda seed: Birch(n_clusters=n_clusters),
        }
        model_constructors = random_model_constructors | no_random_model_constructors

        random_seeds = self.random_seed if isinstance(self.random_seed, list) else [self.random_seed]
        for model_name, model_constructor in random_model_constructors.items():
            val_seed_results = {}
            for seed in random_seeds:
                val_seed_results[seed], _ = self._evaluate_clustering_model(
                    val_embeddings, val_labels, model_constructor(seed)
                )

            median_seed = sorted(
                val_seed_results.items(),
                key=lambda res: res[1][self.main_metric],
                reverse=True,
            )[len(random_seeds) // 2][0]

            val_results[model_name] = val_seed_results[median_seed]
            median_seeds[model_name] = median_seed

        for model_name, model_constructor in no_random_model_constructors.items():
            val_results[model_name], _ = self._evaluate_clustering_model(
                val_embeddings, val_labels, model_constructor(None)
            )
            median_seeds[model_name] = median_seed

        optimal_clustering_model_name = sorted(
            val_results.items(),
            key=lambda res: res[1][self.main_metric],
            reverse=True,
        )[0][0]

        test_scores, test_predictions = self._evaluate_clustering_model(
            test_embeddings,
            test_labels,
            model_constructors[optimal_clustering_model_name](median_seeds[optimal_clustering_model_name]),
        )
        test_results = {optimal_clustering_model_name: test_scores}

        return EvaluationResults(
            metric_name=self.main_metric,
            metric_value=test_results[optimal_clustering_model_name][self.main_metric],
            details={
                "optimal_clustering_model_name": optimal_clustering_model_name,
                "val_scores": val_results,
                "test_scores": test_results,
            },
            predictions=(
                self._format_predictions(self.test_dataset, test_predictions) if self.log_predictions else None
            ),
        )

    @staticmethod
    def _evaluate_clustering_model(
        embeddings: np.ndarray, y_true: list[int], clustering_model: ClusterMixin
    ) -> tuple[dict[str, float], list[int]]:
        y_pred = clustering_model.fit_predict(embeddings)
        h_score, c_score, v_score = homogeneity_completeness_v_measure(
            labels_pred=y_pred, labels_true=np.array(y_true)
        )
        del clustering_model
        return {
            "v_measure_score": v_score,
            "homogeneity_score": h_score,
            "completeness_score": c_score,
        }, y_pred.tolist()

    @staticmethod
    def _format_predictions(dataset: ClusteringDataset, predictions: list[int]) -> list[ClusteringPrediction]:
        return [
            ClusteringPrediction(item.text, item.label, prediction) for item, prediction in zip(dataset, predictions)
        ]
