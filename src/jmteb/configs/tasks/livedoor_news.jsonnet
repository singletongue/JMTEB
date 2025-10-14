{
  livedoor_news: {
    class_path: 'ClusteringEvaluator',
    init_args: {
      val_dataset: {
        class_path: 'HfClusteringDataset',
        init_args: {
          path: 'sbintuitions/JMTEB',
          split: 'validation',
          name: 'livedoor_news',
        },
      },
      test_dataset: {
        class_path: 'HfClusteringDataset',
        init_args: {
          path: 'sbintuitions/JMTEB',
          split: 'test',
          name: 'livedoor_news',
        },
      },
      random_seed: [0, 1, 2, 3, 4],
    },
  },
}
