# Lathe Paper Craft

## Usage
```
ex)
lathe = Lathe("sample.svg")
lathe.cone(20, 10, 10)
```

出力したsvgファイルではオブジェクトがきれいに配置されていないのでInkscape等を用いて編集する

のりしろは印刷後に手描きで追加するのが楽

## Methods
### 一般の回転体
* spiral(cross_section, width, [split=[]])
  * cross_section: 回転体の断面曲線
    * z軸を回転軸として[[x0, z0], [x1, z1], ...]の形で与える
  * width: 帯の幅
  * split: 分割点のリスト(0.0~1.0で与える)
    * [0.3, 0.6]とすると、0.0-0.3, 0.3-0.6, 0.6-1.0の3本の帯ができる
    
### 特殊形状
* cone(bottom_width, top_width, height, [split=[]])
  * 円錐台
  
### その他
* set_step(step)
  * 回転角dθを指定(default: 2π/100)
