# control-jtekt-plc-w-kube
kanban（AION/RabbitMQのアーキテクチャによるメッセージ）から取得したデータを元に、jtekt製のPLCのレジスタにメッセージを送信するマイクロサービスです。  
メッセージの送受信方法およびフォーマットはバイナリ形式に準じています。  

## 1.動作環境  

* OS: Linux  
* CPU:ARM/AMD/Intel  

## 2.対応している接続方式
* Ethernet接続  


## 3.IO

### Input
kanbanからデータを受信します
受け取れるkanbanのパラメータは以下の通りです。
```
status: IO(IN: 0, OUT: 1)
```

### Output
kanbanのデータを元に、PLCへデータの書き込みを行います


## 4.関連するマイクロサービス
control-jtekt-plc-r-kube