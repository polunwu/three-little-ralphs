# Tasks

以下每行 `- ` 開頭的項目為任務，執行 `start.sh` 時會依序寫入 `state.json`。

- 建立基本 CLI 框架：使用 argparse 支援子命令 add / list / done / delete，並印出 "Not implemented" 佔位訊息
- 實作 add 指令：接受 --title（必填）與 --desc（選填），將 todo 以 JSON 格式附加寫入當前資料夾的 todos.json
- 實作 list 指令：讀取 todos.json，以編號列出所有項目（顯示 ID、標題、完成狀態）
- 實作 done 指令：接受 ID，將對應項目的 done 欄位標記為 true 並存回 todos.json
- 實作 delete 指令：接受 ID，從 todos.json 移除對應項目並重新編號
- 新增 --filter 參數至 list 指令，支援 all / pending / done 三種模式過濾輸出
- 為所有指令加上 ANSI 彩色輸出（完成項目灰色、待辦項目綠色、錯誤訊息紅色）
- 撰寫 unittest 測試，覆蓋 add / list / done / delete 的主要流程與邊界情況（例如刪除不存在的 ID）
