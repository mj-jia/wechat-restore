# 微信传图复原

修复微信传输造成的 JPEG 压缩块、振铃与模糊。**纯前端推理**：图片不会上传到任何服务器，断网也能用。

## 用法

1. 打开页面，点选或拖入一张（或多张）微信收到的图片
2. 选择「原尺寸修复」或「修复 + 2 倍放大」
3. 点「开始修复」，拖动分割线看前后对比
4. 「下载这张」或「打包下载全部」

输出文件默认加后缀（`_restored` / `_x2`），不会覆盖原图；JPG 输出会带回原图的 EXIF 与色彩配置。

## 两种模式

| 模式 | 输出尺寸 | 适合 |
|---|---|---|
| 原尺寸修复 | 与输入相同 | 发回微信、手机查看 |
| 修复 + 2 倍放大 | 长宽各 ×2 | 打印、大屏、二次编辑 |

超过 2 倍的部分没有真实细节，所以不提供 4 倍；需要更大尺寸请用原尺寸修复后自行缩放。

## 本地预览

```bash
python site/serve.py 8000
# 浏览器打开 http://127.0.0.1:8000
```

**不要直接双击 index.html**：`file://` 协议下浏览器禁止加载模型文件，必须走 http。

## 部署到 GitHub Pages

1. 把本目录全部文件推到仓库根目录（`main` 分支）
2. 仓库 Settings → Pages → Source 选 `main` → Save
3. 等约 1 分钟，访问 `https://<用户名>.github.io/<仓库名>/`

首次打开会闪一下：`coi-serviceworker.min.js` 需要注册 Service Worker 来注入
`Cross-Origin-Opener-Policy` / `Cross-Origin-Embedder-Policy`，浏览器才允许多线程推理。
之后正常。若用 Cloudflare Pages / Netlify，可直接配置这两个响应头并删掉该 script。

## 文件

| 文件 | 作用 | 大小 |
|---|---|---|
| `index.html` | 全部界面与推理逻辑 | 22 KB |
| `restore1x.onnx` | 原尺寸修复模型 | 4.5 MB |
| `restore2x.onnx` | 2 倍修复模型 | 4.5 MB |
| `ort/` | onnxruntime-web 运行时 | ~36 MB |
| `coi-serviceworker.min.js` | 注入 COOP/COEP，启用多线程 | 2 KB |
| `serve.py` | 本地带头的静态服务器 | 1 KB |

## 技术说明

- 模型：SRVGGNetCompact（64 特征 / 32 卷积，约 1.15M 参数），训练退化按微信实测链路构建：短边 1280 任意比缩放、q≈69 全图统一量化表、4:2:0、二次压缩
- 推理：ONNX Runtime Web，优先 WebGPU，回退 WASM（多线程需 COOP/COEP）
- 大图分块：384px 块、32px 重叠、余弦羽化拼接，避免接缝
- 指标（DIV2K 验证集，q69 压缩图）：原尺寸修复 PSNR +1.5~1.8 dB，LPIPS 降低约一半，块效应 1.12 → 0.89

## 局限

- 传输压缩丢掉的信息无法真正还原，模型只做去伪影与合理重建
- 单线程时大图较慢，建议长边不超过 3000
- 需要支持 WebAssembly 的浏览器（近五年的主流浏览器均可）
