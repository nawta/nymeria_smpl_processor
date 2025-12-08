# Nymeria SMPL Preprocessor

MVNX形式のモーションキャプチャデータをSMPL形式に変換するスクリプト。

## 概要

Nymeriaデータセットの`data_xdata_mvnx`に含まれるMVNXファイルをSMPLパラメータに変換し、`data_smpl_from_xdata_mvnx`に保存します。

## ディレクトリ構成

```
nymeria_smpl_preprocessor/
├── preprocess_mvnx_to_smpl.py  # メインスクリプト
├── mvnx_to_smpl/               # サポートライブラリ
│   └── core/
│       ├── articulate/         # SMPLボディモデル関連
│       └── paths.py            # パス設定
└── README.md
```

## 使用方法

```bash
# デフォルト（ローカルポーズ計算あり、推奨）
python preprocess_mvnx_to_smpl.py

# カスタムパス指定
python preprocess_mvnx_to_smpl.py \
    --input-dir /path/to/data_xdata_mvnx \
    --output-dir /path/to/data_smpl_from_xdata_mvnx

# ローカルポーズなし（非推奨）
python preprocess_mvnx_to_smpl.py --no-use-articulate
```

## 出力形式

各シーケンスディレクトリに以下のファイルが生成されます：

- `smpl_data.npz`: 数値配列のみ（numpy 1.x/2.x互換）
  - `global_poses`: グローバル回転行列 (N, 24, 3, 3)
  - `local_poses`: ローカル回転行列 (N, 24, 3, 3)
  - `root_positions`: ルート位置 (N, 3)

- `smpl_data.json`: メタデータ
  - `joint_names`: ジョイント名リスト
  - `metadata`: フレームレートなど
  - `num_frames`: フレーム数
  - `*_shape`: 各配列の形状

## Numpy互換性について

npzファイルには数値配列のみを保存し、メタデータはJSONに分離しています。
これにより、numpy 1.x と 2.x の間でのpickle互換性問題を回避しています。

## 依存関係

- Python 3.8+
- PyTorch
- NumPy (1.x または 2.x)
- tqdm

## 関連プロジェクト

- [MobilePoser](https://github.com/xxx/MobilePoser): SMPL推定モデル
- Nymeria Dataset: Aria glasses + MVNスーツによるモーションキャプチャデータ
