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
      prefix: 'Identify the topic or theme of the given articles',
      random_seed: [0, 1, 2, 3, 4],
    },
  },
  mewsc16: {
    class_path: 'ClusteringEvaluator',
    init_args: {
      val_dataset: {
        class_path: 'HfClusteringDataset',
        init_args: {
          path: 'sbintuitions/JMTEB',
          split: 'validation',
          name: 'mewsc16_ja',
        },
      },
      test_dataset: {
        class_path: 'HfClusteringDataset',
        init_args: {
          path: 'sbintuitions/JMTEB',
          split: 'test',
          name: 'mewsc16_ja',
        },
      },
      prefix: 'Identify the topic or theme of the given articles',
      random_seed: [0, 1, 2, 3, 4],
    },
  },
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
      prefix: 'Identify the topic or theme of the given articles',
      random_seed: [0, 1, 2, 3, 4],
    },
  },
}
