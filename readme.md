## 仮想サーバー自動構築

1. [Terraform](https://www.terraform.io/) をインストールする。
2. `terraform -v` でバージョンが表示されることを確認する。
    ```bash
    > terraform -v
    Terraform v0.12.5
    ```

3. リポジトリからクローンする。
4. terraform init を実行し、vshpere の Provider がインストールされることを確認する。
    ```bash
    > terraform -v
    Terraform v0.12.5
    + provider.vsphere v1.12.0
    ```
5. `vms.tf` の locals 変数を適宜変更する。
6. `terraform plan` を実行し、エラーがないことを確認する。
7. `terraform apply` を実行し、対象の vCenter 上に仮想サーバーが構築されることを確認する。

## 複数のサーバーの作り方
**Note:** `vms.tf` の `resource` ブロックが仮想サーバーのインスタンスの設定を定義している。

1. 作成したいサーバーの分だけ `resource` のブロックをコピーする。
2. サーバーのパラメータは変数(`num_cpus = "${local.cpu-1}"`など)で定義されているので、`locals` ブロックで適宜追加、変更を行う。
3. パラメータの詳細については、[ドキュメント](https://www.terraform.io/docs/providers/vsphere/r/virtual_machine.html)を参照。

## パラメータシートの自動生成
1. python 3 がインストールされていることを確認する。
2. 関連するパッケージをインストールする。
    ```
    pip install -r requirements.txt
    ```
3. `terraform apply` 実行後に、以下のコマンドを実行する。
    ```
    python .\docs\main.py
    ```
4. ルートフォルダにパラメータシート.xlsx が生成されていることを確認する。
5. 適宜、パラメータシートを修正する。
