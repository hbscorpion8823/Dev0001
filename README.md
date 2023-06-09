# このゲームについて  
このゲームはKivyで作成した2Dアクションゲームです。  
スワイプするとキャラクターが動きます。  
敵を倒したり、アイテムを取ったりしながらクリアを目指して下さい  
PCとAndroidで遊べます  

## 効果音  

[効果音ラボ](https://soundeffect-lab.info/)  

## 画像  
[Game-icons.net](https://game-icons.net/)  
(explode.zipは私の手製です。ご自由にお使い下さい)  

## 動作環境セットアップ手順  

### kivy, buildozerのインストール    
[公式のインストール手順](https://kivy.org/doc/stable/gettingstarted/installation.html)  
python3、python3-pipがインストールされている場合は  
```shell  
$ pip install kivy
```  
のコマンドでkivyをインストールできる。  
buildozer(android端末へのインストール用？ツール)も同様に  
```shell  
$ pip install buildozer
```  
のコマンドでインストールできる。インストールが成功していれば  
```shell  
$ cd <プロジェクトのルートディレクトリ>
$ python3 main.py
```  
を実行すると、PCでも動かせます  
kivyアプリケーションで画像や音声を扱う際にエラーが発生する場合は [Githubのissues](https://github.com/kivy/kivy/issues/6536#issuecomment-747781482) を参考に、いったんkivyをアンインストールしてからノンバイナリオプションを指定して再インストールするとエラーを解消することができる(私の場合はそれで解決しました)  

### Android端末へのインストール  

**※buildozer.specを自分の環境に合わせて修正されていることが前提です**  
buildozer.sample.specをリネームし、自分の環境に合わせて修正して下さい  
Android端末にインストールするapkファイルは  
```shell  
$ cd <アプリケーションのルートディレクトリ>  
$ buildozer -v android debug
```  
で作成できる。debugはデバッグ用のapkファイルを指定するターゲットコマンドで、releaseを指定することによりリリース用のapkファイルを作成することもできる。  
```shell  
$ buildozer android deploy run logcat
```  
のコマンドを実行することによって、作成したapkファイルをAndroid端末上で動かすことができる。  
(Android端末を、USBデバッグを許可した状態で接続すること)  