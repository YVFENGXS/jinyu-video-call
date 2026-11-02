# 瑾瑜

浏览器里的 Live2D 视频通话舞台：白天/夜晚房间背景、顶部通话条、右上角我方小窗、底部圆形控制栏，接摄像头与屏幕共享，支持语音对话、舞台动作、头部姿态和「看着画面自己开口」。

作者：**yvfeng**

## 功能

- **视频通话外观**：房间背景随昼夜自动切换，也可手动切换；模型按顶栏/底栏/右侧面板留出安全区。
- **摄像头**：页面打开并点击后取帧，按人物/环境判读，不后台截屏。
- **屏幕共享**：可共享整个屏幕或单个窗口；长截图自动切段，优先读窗口、报错、文件、文字。
- **语音对话**：浏览器录音 → ASR → 记忆/人设 → 回复 → 首句 TTS，剩余句子续合成。
- **舞台控制**：模型可用 `[[表情:...]]`、`[[动作:...]]`、`[[转头:左]]`、`[[点头:3]]` 等标记控制表情、动作和头姿。
- **主动开口**：画面每分钟至少补一帧，AI 根据刚看到的内容决定要不要主动说一句；不想说就回 `[[pass]]`。
- **跨窗口发话**：QQ/桌宠可通过 `/call/say` 把一句话推到通话页播放。

## 目录

```
jinyu-video-call/
├── call_server.py          # FastAPI 服务：静态舞台 + 视觉 + 语音 + 舞台状态
├── call_voice.py           # ASR / TTS
├── screen_vision.py        # 屏幕 / 摄像头画面判读
├── jinyu_memory/core/      # 运行所需的记忆核心依赖
│   ├── persona.py          #   人设单源
│   ├── rp_skeleton.py      #   SQLite 中间件
│   ├── llm.py              #   OpenAI 兼容客户端
│   └── ...
├── web/live2d/             # 前端舞台（HTML/CSS/JS、背景图、第三方库）
├── .env.example
├── requirements.txt
└── LICENSE
```

## 运行

需要 Python 3.10+。

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # Windows: copy .env.example .env
# 编辑 .env，填入模型、视觉、语音识别的密钥

python call_server.py --port 8790 --env-file .env
```

打开 <http://127.0.0.1:8790/>。

### Live2D 模型

**仓库不包含 Live2D 模型文件**，默认从下面这个路径加载：

```
web/live2d/models/jinyu/大肥鱼.model3.json
```

如果你使用自己的模型，把模型目录放到 `web/live2d/models/` 下，并修改 [app.js](web/live2d/app.js) 顶部的 `MODEL_URL` 和 `MODEL_DIR`。

示例使用的 DeepSeek-chan（大肥鱼）模型由原作者免费配布，版权与使用条件归原作者所有，请自行从原作者处获取并遵守其使用须知，不要在本仓库中重新分发模型文件。

## 配置

| 变量 | 说明 |
|---|---|
| `RP_FRONT_KEY` / `RP_FRONT_MODEL` | 前台对话模型（OpenAI 兼容） |
| `RP_BACK_KEY` / `RP_BACK_MODEL` | 后台模型；主动开口默认用它 |
| `RP_LLM_BASE` | 模型接口地址，留空用默认 |
| `RP_GLM_KEY` / `RP_GLM_MODEL` | 视觉判读（智谱 GLM） |
| `RP_ASR_KEY` / `RP_ASR_BASE` / `RP_ASR_MODEL` | 语音识别（SiliconFlow） |
| `RP_TTS_VOICE` / `RP_TTS_DIR` | edge-tts 音色与缓存目录 |
| `RP_SESSION` | 默认会话键，默认 `local-user` |
| `RP_DB` | 本地 SQLite 路径，默认 `desktop_memory.db` |
| `RP_HOST_BASE` / `RP_HOST_TOKEN` | 可选：接到已有的瑾瑜 QQ 宿主进程 |
| `RP_CALL_HOST` / `RP_CALL_PORT` | 监听地址与端口 |
| `RP_WIN_TOKEN` | `/call/say` 的跨窗口令牌；不设时只收本机回环 |

**记忆写入**：设置 `RP_HOST_BASE` + `RP_HOST_TOKEN` 时，通话服务通过宿主接口读写记忆，本进程不碰 SQLite；不设置时使用本地 `desktop_memory.db`。同一个数据库不要同时让两个进程写。

## 接口

| 方法 | 路径 | 作用 |
|---|---|---|
| GET | `/health` | 视觉 / 模型 / ASR / TTS 就绪状态 |
| POST | `/vision/frame` | 读一帧屏幕或摄像头 |
| POST | `/vision/ask` | 带着画面回答一个问题 |
| POST | `/call/turn` | 一轮语音或文字对话 |
| POST | `/call/proactive` | AI 看画面，自己决定要不要开口 |
| POST | `/call/tts` | 剩余句子补合成 |
| POST | `/stage/state` | 前端上报当前表情/动作/头姿 |
| GET | `/call/inbox` | 通话页取跨窗口待播的话 |
| POST | `/call/say` | QQ/桌宠推一句话到通话页 |

## 隐私

- 画面帧只在内存里判读，不落盘。
- 摄像头只在页面打开且用户点击后取帧，不做后台截屏。
- 音频只读一次，不落盘（TTS 缓存除外）。
- `.env`、数据库、模型文件都不入版本库。

## 第三方组件与致谢

- Live2D Cubism Core：归 Live2D Inc. 所有，使用需遵守 Live2D 许可。
- PixiJS：MIT License。
- pixi-live2d-display：MIT License。
- **[YVFENGXS/Jinyv-memory](https://github.com/YVFENGXS/Jinyv-memory)** —— `jinyu_memory/core/` 的记忆核心来自该仓库（MIT）；其分层记忆与检索设计参考过 [SeekMemory](https://github.com/NeverENG/SeekMemory) 与 dsh-fish，工程实践参考过 [AstrBot](https://github.com/AstrBotDevs/AstrBot)，均未复制代码。
- **[opencode-acp](https://github.com/ranxianglei/opencode-acp)**、**[billion-context-pi](https://github.com/ranxianglei/billion-context-pi)**、**[billion-context](https://github.com/ranxianglei/billion-context)** —— 长会话上下文压缩思路参考（模型驱动、增量分层压缩），未复制代码。
- **DeepSeek-chan（大肥鱼）Live2D 模型** —— 原画 / 拆分：神宫凉子，Live2D 建模：霓虹猫_NeonNeko；模型不随仓库分发，版权与使用条件归原作者。

各自的具体条款以对应项目的 LICENSE 为准；本仓库只借鉴设计思路，未复制上述参考项目的源码。

## License

MIT License，Copyright (c) 2026 yvfeng。详见 [LICENSE](LICENSE)。
