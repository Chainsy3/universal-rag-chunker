# 项目介绍页

静态网站源文件位于 site/；不依赖构建工具、第三方字体或分析脚本。输出示例切换与复制命令只在浏览器本地运行，不上传文档。

GitHub Pages 工作流：.github/workflows/pages.yml。公开仓库需在 Settings → Pages → Build and deployment 中将 Source 设置为 GitHub Actions。之后 main 上的 site/ 变更会自动部署。

计划站点地址：https://Chainsy3.github.io/universal-rag-chunker/ 。只有 GitHub Pages 部署成功并验证返回页面后，才应将其描述为已上线。

本地预览：在项目根目录运行 `python -m http.server 8765 --directory site`，浏览器打开 http://localhost:8765 。这是项目说明页，不提供在线文件解析服务。
