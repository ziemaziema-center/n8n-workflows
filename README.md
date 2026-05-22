# TRUE AUTONOMOUS CONTROLLER

## English

TRUE AUTONOMOUS CONTROLLER is a bounded autonomous orchestration layer that turns a user command into a company-style execution loop:

Telegram command -> n8n intake -> HQ planning -> queued runtime task -> tmux/Codex execution -> reviewer/retry -> Telegram final report.

Use it when you want Codex to behave like an operating company instead of a one-shot coding assistant. The controller keeps task state, records deferred gates, runs offline validation, writes reports, and hands off the next executable step.

Recommended operator command:

```text
/work <objective>
```

Example:

```text
/work Improve the autonomous controller runtime, run validations, fix bugs, and report the result in Korean.
```

Safety model:
- Safe local/offline work continues without repeated approval.
- Live production actions, secrets, AWS mutation, workflow activation, live publishing, and live trading stay behind explicit gates.
- One blocked live/credential/network item must not stop the whole task.

README policy:
Every new or edited README in this project must include English, French, Spanish, Korean, and Chinese sections in the same file, unless it is a third-party vendored README.

## Français

TRUE AUTONOMOUS CONTROLLER est une couche d'orchestration autonome bornée qui transforme une commande utilisateur en boucle d'exécution de type entreprise :

commande Telegram -> réception n8n -> planification HQ -> tâche en file d'attente -> exécution tmux/Codex -> revue/réessai -> rapport final Telegram.

Utilisez-le lorsque vous voulez que Codex agisse comme une équipe opérationnelle plutôt que comme un assistant de codage ponctuel. Le contrôleur conserve l'état des tâches, note les portes différées, lance les validations hors ligne, écrit les rapports et prépare la prochaine étape exécutable.

Commande opérateur recommandée :

```text
/work <objectif>
```

Exemple :

```text
/work Improve the autonomous controller runtime, run validations, fix bugs, and report the result in Korean.
```

Modèle de sécurité :
- Le travail local/hors ligne sûr continue sans approbations répétées.
- Les actions de production, secrets, mutations AWS, activations de workflows, publications live et opérations de trading restent derrière des portes explicites.
- Un élément live/credential/network bloqué ne doit pas arrêter toute la tâche.

Politique README :
Chaque README nouveau ou modifié dans ce projet doit contenir des sections en anglais, français, espagnol, coréen et chinois dans le même fichier, sauf s'il s'agit d'un README tiers fourni par un vendeur.

## Español

TRUE AUTONOMOUS CONTROLLER es una capa de orquestación autónoma y acotada que convierte una orden del usuario en un ciclo de ejecución tipo empresa:

comando de Telegram -> entrada de n8n -> planificación HQ -> tarea en cola -> ejecución tmux/Codex -> revisión/reintento -> informe final por Telegram.

Úsalo cuando quieras que Codex funcione como una compañía operativa y no como un asistente de programación de una sola ejecución. El controlador conserva el estado, registra puertas diferidas, ejecuta validaciones offline, escribe informes y deja lista la siguiente acción ejecutable.

Comando recomendado:

```text
/work <objetivo>
```

Ejemplo:

```text
/work Improve the autonomous controller runtime, run validations, fix bugs, and report the result in Korean.
```

Modelo de seguridad:
- El trabajo local/offline seguro continúa sin aprobaciones repetidas.
- Producción, secretos, cambios AWS, activación de workflows, publicaciones live y trading live siguen detrás de puertas explícitas.
- Un elemento live/credential/network bloqueado no debe detener toda la tarea.

Política README:
Cada README nuevo o editado en este proyecto debe incluir secciones en inglés, francés, español, coreano y chino en el mismo archivo, salvo README de terceros incluidos como vendored.

## 한국어

TRUE AUTONOMOUS CONTROLLER는 사용자의 한 줄 명령을 회사형 실행 루프로 바꾸는 bounded autonomous orchestration layer입니다.

Telegram 명령 -> n8n 접수 -> HQ 기획 -> runtime queue 등록 -> tmux/Codex 실행 -> reviewer/retry -> Telegram 최종 보고.

Codex가 단발성 코딩 도우미가 아니라, 상태를 기억하고 역할을 나누고 검증하며 다음 작업까지 인계하는 운영팀처럼 움직이게 만드는 것이 목표입니다.

권장 명령:

```text
/work <목표>
```

예시:

```text
/work autonomous controller runtime을 개선하고, 검증하고, 버그를 고친 뒤 한국어로 최종 보고해.
```

안전 모델:
- 안전한 local/offline 작업은 반복 승인 없이 계속 진행합니다.
- production 작업, secret 접근, AWS 변경, workflow 활성화, live publishing, live trading은 명확한 gate 뒤에 둡니다.
- live/credential/network 항목 하나가 막혀도 전체 작업을 멈추지 않습니다.

README 정책:
이 프로젝트에서 README 파일을 새로 만들거나 수정할 때는, 사용자가 따로 말하지 않아도 영어, 불어, 스페인어, 한국어, 중국어 5개 언어 섹션을 같은 파일 안에 반드시 포함합니다. 단, 외부 vendored README는 예외입니다.

## 中文

TRUE AUTONOMOUS CONTROLLER 是一个有边界的自主编排层，把用户命令转换成公司式执行循环：

Telegram 命令 -> n8n 接收 -> HQ 规划 -> 运行队列任务 -> tmux/Codex 执行 -> 审查/重试 -> Telegram 最终报告。

当你希望 Codex 像一个运营团队而不是一次性代码助手时，可以使用它。控制器会保存任务状态、记录延迟门、运行离线验证、生成报告，并交接下一步可执行任务。

推荐操作命令：

```text
/work <目标>
```

示例：

```text
/work Improve the autonomous controller runtime, run validations, fix bugs, and report the result in Korean.
```

安全模型：
- 安全的本地/离线工作可以继续进行，不需要重复批准。
- 生产操作、密钥、AWS 变更、workflow 激活、实时发布和实时交易必须通过明确的 gate。
- 一个 live/credential/network 项目被阻塞，不应停止整个任务。

README 政策：
本项目中新建或修改任何 README 时，必须在同一文件中包含英文、法文、西班牙文、韩文和中文五种语言的说明，第三方 vendored README 除外。
