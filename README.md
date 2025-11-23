# IBA Note

Pythonで作られたオフラインWebツールで、IBAの内容を記録するための小さなツールです。
カスタマイズ可能なIC/RC画像とデータ、メモの追加・閲覧・編集機能を含みます。

A small offline tool built with Python for recording what you get in IBA.
Includes customizable IC/RC images, introduce; notes adding, viewing, and editing.

一個基於python建立離線網頁，用來紀錄IBA內容的小工具。
包含可自訂的IC/RC圖片與資料，留言的新增與查看編輯功能。

---

- **Imaginary Cast Tab (IC)**  
  - IC画像と内容は公式サイト (https://imaginary-base.jp/cast/) から
  
  - IC images and content are obtained from the official website.(https://imaginary-base.jp/cast/)
  
  - IC圖片與內容由官方網站(https://imaginary-base.jp/cast/)取得。

- **Real Cast Tab (RC)**  
  - 未完成で、今後追加予定です。
  
  - Not completed yet, planned to be added later.
  
  - 尚未完成，預計於後續追加。

- **Note Tab (Note)**  
  - IC / RCタブで選択された項目のみ表示
  - 各行に1つのキャストを表示
  - メモの閲覧・編集・削除
  - メモは新しい順に表示
  - 改行に対応
  - 編集用メモ欄は追加用メモ欄と同じサイズ
  - メモはデフォルトで非表示、キャストをクリックすると表示

  - Only displays selected items from the IC / RC tabs.
  - Each row shows one Cast.
  - View, edit, and delete notes.
  - Notes are ordered from newest to oldest.
  - Supports line breaks.
  - Notes are hidden by default and shown by clicking the Cast.

  - 僅顯示 IC / RC 分頁中被選中的
  - 每列顯示一個 Cast  
  - 查看、編輯、刪除留言  
  - 留言時間由新到舊  
  - 支援換行  
  - 編輯留言欄位大小與新增留言欄位一致  
  - 預設留言隱藏，點擊 Cast 顯示

- **Guide & Set**  
  - 公式関連ウェブページへのリンク
  
  - Links to official related web pages

  - 官方相關網頁連結  

- **今後の更新予定 / Planned Future Updates**
  - Noteタブのボタン配置の調整
  - RCタブの機能追加
  - 多言語対応
  - 完全オフライン版（機能の一部を削減）
  - ICスクレイパーの更新（検討中）

  - Adjust button layout in the Note tab
  - RC tab functionality
  - Multi-language support
  - Fully offline web version (with some feature reductions)
  - IC data Web scraper updates (under consideration)

  - Note分頁按鈕排版調整
  - RC 分頁功能
  - 多國語言支援
  - 純離線網頁版本(部分功能刪減)
  - IC 爬蟲更新(考慮中)

---

## 使用方法 / Usage Instructions

1. Android / iOS / x86 など、お好みの環境にPython実行環境を構築してください。
2. プロジェクトを完全にダウンロードし、ファイル構造を変更しないでください。
（注意：Androidでは.dbファイルが正しくコピーできない場合があります。拡張子を一度削除してコピー後に戻すと良いです。）
3. 実行環境にFlaskライブラリをインストール
```bash
pip install flask
```
4. IBA_note.py を実行すると、ブラウザが自動で開きます。
---
1. Set up a Python execution environment on Android / iOS / x86 according to your preference.
2. Download the project completely and make sure the file structure remains unchanged.
    (Note: On Android, .db files may not copy correctly. You can remove the extension before copying and add it back afterward.)
3. Install the Flask library in your environment
```bash
pip install flask
```
4. Run IBA_note.py, the browser will open automatically.
---
1. 建立python 執行環境 Android / IOS / X86 ，請依各自喜好建立。
2. 下載專案，請完整下載，並確保檔案結構無變化。
    (注意：Android可能遇到.db檔案無法正確複製，可先刪除副檔名，複製後再補回。)
3. 在自己的執行環境安裝flask庫
```bash
pip install flask
```
4. 執行 IBA_note.py，瀏覽器將自行開啟。

## Feedback
プログラムのバグや機能リクエストは自由に報告してください。時間があるときに対応します。

Feel free to report program bugs or feature requests, I will handle them in my spare time.

歡迎提出程序bug與功能需求，我會在空閒的時間進行處理。

## Copyright

 - IC画像とテキスト内容は ©IMAGINARY BASE PROJECT https://imaginary-base.jp/
 - コード部分は村人Qによる作成で、GPL v3ライセンスの下で公開されています。
 
 - IC images and text content are ©IMAGINARY BASE PROJECT https://imaginary-base.jp/
 - Code by Murabito Q, licensed under GPL v3.

 - IC圖片與文字內容屬於 ©IMAGINARY BASE PROJECT https://imaginary-base.jp/
 - code由村人Q完成，使用GPL v3授權。

