{
  sib200_clustering: {
    class_path: 'ClusteringEvaluator',
    init_args: {
      val_dataset: {
        class_path: 'HfClusteringDataset',
        init_args: {
          path: 'sbintuitions/JMTEB',
          split: 'validation',
          name: 'sib200_japanese_clustering',
        },
      },
      test_dataset: {
        class_path: 'HfClusteringDataset',
        init_args: {
          path: 'sbintuitions/JMTEB',
          split: 'test',
          name: 'sib200_japanese_clustering',
        },
      },
      random_seed: [0, 1, 2, 3, 4],
    },
  },
}
