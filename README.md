# 開発アプリ

![Screen-Recording-2025-02-16-at-11.30.15 AM_1.gif](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2674841/cc67382b-c531-449a-92e3-0b697b1b7769.gif)

# 概要
Python（Flask）と機械学習を使用したフルスタック開発を実施。
講師は酒井潤さんで、レストラン推薦アプリケーション「roboter2」の構築を行う。
書籍「シリコンバレー一流プログラマーが教える Python プロフェッショナル大全」と有料のYouTube解説どうgを参考にしながら、学習を行なった。

# 学習教材
## YouTube
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2674841/5ad60a11-9c83-4f91-9bc1-add616f549b4.png)

https://www.youtube.com/watch?v=oP6UIBRjbEc&list=PLq-JeSNkOKBR4nihDUziGfEvMBMyi9X3v

## 書籍
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2674841/2d0547c1-4584-4e9f-a8fc-88c8df5390ee.png)

www.amazon.co.jp/dp/4046057548

# 内容
以下のカリキュラムで実施。
ポイントは、20.で機械学習を取り入れている点。

1. はじめに
1. Macに開発環境を設定する
1. Windowsに開発環境設定をする
1. 応用アプリのrobterの確認と新しく作るroboter2の概要
1. 開発する手順とMVCイメージ
1. logging設定
1. ユーザーモデルの作成
1. レストランモデルの作成
1. レイトモデルの作成
1. FlaskのWebサーバーの起動とhello htmlの作成
1. FlaskでのPOST処理
1. スタイルの変更
1. templateの共有化
1. 評価フォームの作成
1. Flask WFTプラグインによるフォーム作成
1. テンプレート、コントローラー、モデルの連携
1. レストランモデルのget or create
1. Rateテーベルのupdate or create
1. レコメンデーションの画面作成
1. 機械学習でレコメンデーションをする
1. コードの見直し
1. コードのフォーマットの修正
1. 最後に

## 開発したアプリ
# TOP画面
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2674841/f69a1e9f-7ba8-4107-adf4-17e000219757.png)

# おすすめレストラン紹介画面
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2674841/5167086e-6a22-4898-bab0-4cbb8a3f2ed3.png)

# レストラン評価画面
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2674841/b263478f-3734-4986-bdd9-6fc3657b8dbf.png)

# レストラン評価完了画面
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2674841/572f87a2-e4ac-481d-8498-2605d38ae85d.png)

# おすすめ機能の解説
レストランとユーザーの評価するrate.pyにrecommend_restaurantを実装

## テーブル構成
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2674841/94e89cb3-0144-4b51-834d-b12707526182.png)



## 関数の概要
機能: ユーザーの過去のレストラン評価データに基づいて、そのユーザーが好む可能性の高いレストランを推薦します。
入力: ユーザーオブジェクト (User)
出力: おすすめのレストラン名のリスト

## 推薦の流れ
### 1. 設定による推薦方法の切り替え
RECOMMEND_ENGIN_ENABLEがtrueの場合、シンプルな推薦処理を実施。falseの場合は機械学習による推薦を実施。
```
if not settings.RECOMMEND_ENGIN_ENABLE:
    # シンプルな推薦処理
else:
    # 機械学習による推薦処理
```

### 2. シンプルな推薦処理

```
session = database.connnect_db()
recommend = [
    r.name
    for r in session.query(Restaurant).all()[:TOP_RECOMMEND_RESTAURANT_NUM]
]
session.close()
return recommend
```
データベースからすべてのレストラン情報を取得し、最初の TOP_RECOMMEND_RESTAURANT_NUM 個のレストラン名をリストとして返します。

### 3. 機械学習による推薦処理
3.1 データベースからユーザーの評価データ (rate テーブル) を取得し、pandas DataFrame df に格納します。
```
session = database.connnect_db()
df = pd.read_sql("SELECT user_id, restaurant_id, value from rate", session.bind)
session.close()
```

3.2 評価データを surprise ライブラリのデータ形式に変換します。
```
dataset_columns = ["user_id", "restaurant_id", "value"]
reader = Reader()
data = Dataset.load_from_df(df[dataset_columns], reader)
```

3.3 NormalPredictor を使用して、データの基本的な検証を行います。
エラーが発生した場合は、ログに記録し、None を返します。

```
try:
    cross_validate(NormalPredictor(), data, cv=2)
except ValueError as ex:
    logger.error({"action": "recommended_restaurant", "error": ex})
    return None
```
3.4 SVD モデルを訓練します。
```
svd = SVD()
trainset = data.build_full_trainset()
svd.fit(trainset)
```
3.5 各レストランに対するユーザーの予測評価値を計算し、予測評価値に基づいてレストランをランキングします。
```
predict_df = df.copy()
item_id = "restaurant_id"
predict_df["Predicted_Score"] = predict_df[item_id].apply(
    lambda x: svd.predict(user.id, x).est
)
predict_df = predict_df.sort_values(by=["Predicted_Score"], ascending=False)
predict_df = predict_df.drop_duplicates(subset=item_id)
```
3.6 予測結果の DataFrame が None の場合は、ログに記録し、空のリストを返します。
```
if predict_df is None:
    logger.error(
        {"action": "recommended_restaurant", "status": "no predict data"}
    )
    return []
```

3.7 ランキング上位のレストラン名をリストとして抽出します。

```
recommended_restaurants = []
for index, row in predict_df.iterrows():
    restaurant_id = int(row["restaurant_id"])
    restaurant = Restaurant.get(restaurant_id)
    recommended_restaurants.append(restaurant.name)
        return recommended_restaurants[:TOP_RECOMMEND_RESTAURANT_NUM]
```

### 4.まとめ
推薦アルゴリズム: 設定によってシンプルな推薦と機械学習を用いた推薦を切り替えます。
機械学習モデル: surprise ライブラリの SVD モデルを使用しています。
評価データ: データベースの rate テーブルから評価データを取得します。
エラーハンドリング: エラーが発生した場合、ログに記録し、適切な値を返します。
ログ出力: logger.error を使用してエラー情報をログに出力します。

