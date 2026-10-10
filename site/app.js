"use strict";
const english = document.documentElement.lang === "en";
const samples = {
  pdf: {schema_version:"1.1",kind:"text",text:"运行安装命令。",metadata:{"core.source_locations":[{kind:"page",page:3}]}},
  word: {schema_version:"1.1",kind:"table",text:"R2C1: 示例\n",metadata:{"core.source_locations":[{kind:"docx",body_index:4,row:2}]}},
  excel: {schema_version:"1.1",kind:"table",text:"A2: 示例\nB2: 123\n",metadata:{"core.source_locations":[{kind:"sheet",sheet_name:"登记",row:2,column_start:1,column_end:2}]}}
};
if (english) {
  samples.pdf.text = "Run the installation command.";
  samples.word.text = "R2C1: Example\n";
  samples.excel.text = "A2: Example\nB2: 123\n";
  samples.excel.metadata["core.source_locations"][0].sheet_name = "Register";
}
const output = document.getElementById("output-code");
document.querySelectorAll("[data-example]").forEach(button => {
  button.addEventListener("click", () => {
    output.textContent = JSON.stringify(samples[button.dataset.example],null,2);
    document.querySelectorAll("[data-example]").forEach(item => {
      const active = item === button;
      item.classList.toggle("active",active);
      item.setAttribute("aria-pressed",String(active));
    });
  });
});
document.getElementById("copy-command").addEventListener("click", async () => {
  const status = document.getElementById("copy-status");
  try {
    await navigator.clipboard.writeText(document.getElementById("install-code").textContent);
    status.textContent = english ? "Copied. Run these commands in a Python 3.11+ virtual environment." : "命令已复制。请在 Python 3.11+ 的虚拟环境中执行。";
  } catch {
    status.textContent = english ? "Automatic copying is unavailable. Select and copy the commands above." : "当前浏览器不允许自动复制，请选中上方命令手动复制。";
  }
});
