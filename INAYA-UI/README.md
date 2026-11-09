# INAYA UI — React + Vite frontend prototype

This is an isolated frontend prototype. It does **not** overwrite or modify your existing `D:\INAYA` project.

## Features

- Responsive, dark futuristic INAYA dashboard with animated orb and waveform
- State-driven IDLE / LISTENING / THINKING / SPEAKING / ERROR states
- Local mock chat responses, loading indicator, Enter-to-send and clear chat
- DEMO-labeled activity feed, task history and progress display
- Settings modal with persisted theme, glow intensity, animations, sound, voice and speech rate
- Browser speech synthesis voice test and optional spoken mock replies
- Microphone dictation initiated only after clicking the microphone button
- System status panel that clearly distinguishes browser capabilities from unconnected AI / computer control
- No API key required; no AI backend connected

## Run locally

Requires Node.js 20+ and npm. From this folder:

```powershell
npm install
npm run dev
```

Open the local URL Vite prints (normally `http://localhost:5173`). To create a production build:

```powershell
npm run build
```

## Notes

- Chat answers are local mock responses, never real model output.
- Browser speech synthesis varies by browser and operating system.
- Speech recognition is supported only by some browsers and may require HTTPS or localhost and microphone permission.
- The browser cannot minimize or close its own tab; those controls explain that limitation instead.
- Google Fonts are loaded remotely when network access is available; system font fallbacks are included.

## Safe integration into an existing project

This folder is intentionally standalone until the existing `D:\INAYA` files can be inspected. Do not replace the current app blindly. Upload a ZIP of your existing project (excluding `node_modules` and secrets such as `.env` files) to adapt this interface while preserving your existing functionality.
