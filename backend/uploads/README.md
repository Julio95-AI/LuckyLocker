# 客服二维码存放说明

## 默认二维码设置

请将客服微信二维码图片保存为：

```
default_qrcode.png
```

放置在当前目录（`backend/uploads/`）下。

## 要求

- 文件名必须是：`default_qrcode.png`
- 支持格式：PNG、JPG、GIF
- 建议尺寸：至少 300x300 像素以保证清晰度
- 前端显示尺寸：180x180 像素

## 自定义上传

也可以通过管理后台 > 客服二维码 页面上传自定义二维码，上传后会自动替换默认二维码。

上传的文件会保存为：`service_qrcode_YYYYMMDDHHMMSS.png`
