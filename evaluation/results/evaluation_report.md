# 评测报告

生成时间: 2026-03-18 14:01:18

## 1. 数据集概览

| 项目 | 值 |
|---|---|
| 样本总数 | 40 |
| 黑样本 (label=1) | 20 |
| 白样本 (label=0) | 20 |
| 黑白比例 | 1:1 |
| 含图片样本 | 28 |
| 含音频样本 | 4 |

## 2. 诈骗类型覆盖 (12 种)

| 诈骗类型 | 数量 |
|---|---|
| 综合型电信网络诈骗 | 8 |
| 邮寄黄金投资诈骗 | 2 |
| 校园综合诈骗 | 1 |
| 婚恋交友诈骗 | 1 |
| 交友引流刷单诈骗 | 1 |
| 刷单返利诈骗 | 1 |
| 节日红包诈骗 | 1 |
| 兼职招聘诈骗 | 1 |
| 投资理财诈骗 | 1 |
| AI冒充亲属诈骗 | 1 |
| 假中奖诈骗 | 1 |
| 冒充班主任收费诈骗 | 1 |

## 3. 数据获取与处理

- **黑样本构建**: 以公开反诈案例、警情通报、反诈宣传报道等真实公开材料为基础，围绕投资理财、刷单返利、婚恋交友、冒充班主任收费、兼职招聘、AI 冒充亲属等诈骗场景进行人工筛选和标签整理。
- **白样本构建**: 以公开正常新闻、社会资讯、政务信息、科技教育类报道为基础，通过新闻抓取脚本获取候选内容后，再进行人工复核，剔除与诈骗风险强相关的文本，保留正常语义样本。
- **文本清洗流程**: 原始样本先以 txt 形式归档，再统一转换为 `evaluation/dataset.json`。转换过程中完成字段标准化、空白折叠、缺失内容补齐、标签修正与 `case_id` 统一命名。
- **图片与音频对齐**: 图片和音频采用与样本 `case_id` 同名的文件命名规则，分别放置于 `evaluation/images/` 与 `evaluation/audio/`，评测脚本运行时按文件名自动匹配对应模态资源。
- **多模态覆盖方式**: 当前评测集以文本为基础样本集，在此基础上补充部分图片样本和音频样本，用于验证系统在文本、图像、语音三类输入下的识别表现。
- **数据构建相关脚本**:
  - 候选样本抓取: `scripts/fetch_sogou_wechat_dataset.py`
  - 微信文章正文提取: `scripts/extract_article_content.py`
  - txt 转结构化 JSON: `scripts/convert_txt_dataset_to_json.py`
  - 图片/音频资源挂载: `scripts/attach_media_assets_to_dataset.py`
  - 提交版数据集整理: `scripts/build_submission_dataset.py`

## 4. 评测方法

- **Phase 1 (Agent 综合分析)**: 调用 `POST /api/v1/agent/analyze`，将文本、图片、音频作为联合输入，由多模态智能体直接输出风险等级与综合判断结果。
- **Phase 2 (Detection 逐模态检测)**: 分别调用 `ai-text`、`ai-image`、`audio-risk` 三类专项检测接口，记录各模态风险结果，并以最高风险等级作为当前样本的综合判定结果。
- **标签映射规则**: `risk_level ∈ {medium, high}` 映射为黑样本（1），`low` 映射为白样本（0），用于统一计算 Accuracy、Precision、Recall 与 F1-Score。
- **鉴权方式**: 评测脚本通过账号密码自动登录后端服务，获取 Bearer Token 后执行批量测评。

## 5. Phase 1 — Agent 综合分析结果

| 指标 | 值 |
|---|---|
| Accuracy | 0.7250 |
| Precision | 0.6452 |
| Recall | 1.0000 |
| F1-Score | 0.7843 |

### 混淆矩阵

| | 预测=黑 | 预测=白 |
|---|---|---|
| 实际=黑 | 20 | 0 |
| 实际=白 | 11 | 9 |

## 6. Phase 2 — Detection 逐模态检测结果

| 指标 | 值 |
|---|---|
| Accuracy | 0.8250 |
| Precision | 0.8095 |
| Recall | 0.8500 |
| F1-Score | 0.8293 |

### 混淆矩阵

| | 预测=黑 | 预测=白 |
|---|---|---|
| 实际=黑 | 17 | 3 |
| 实际=白 | 4 | 16 |

## 7. 逐条结果明细

| case_id | 标签 | 模态 | P1风险 | P1预测 | P1正确 | 文本风险 | 图片风险 | 音频风险 | P2综合风险 | P2预测 | P2正确 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TXT_BLACK_001 | 黑 | text+image | high | 黑 | ✓ | high | high | - | high | 黑 | ✓ |
| TXT_BLACK_002 | 黑 | text+image | high | 黑 | ✓ | low | high | - | high | 黑 | ✓ |
| TXT_BLACK_003 | 黑 | text+image | high | 黑 | ✓ | low | high | - | high | 黑 | ✓ |
| TXT_BLACK_004 | 黑 | text+image | medium | 黑 | ✓ | medium | low | - | medium | 黑 | ✓ |
| TXT_BLACK_005 | 黑 | text+image+audio | high | 黑 | ✓ | low | high | low | high | 黑 | ✓ |
| TXT_BLACK_006 | 黑 | text+image | high | 黑 | ✓ | low | high | - | high | 黑 | ✓ |
| TXT_BLACK_007 | 黑 | text+image | high | 黑 | ✓ | low | low | - | low | 白 | ✗ |
| TXT_BLACK_008 | 黑 | text+image | medium | 黑 | ✓ | low | low | - | low | 白 | ✗ |
| TXT_BLACK_009 | 黑 | text+image | high | 黑 | ✓ | high | low | - | high | 黑 | ✓ |
| TXT_BLACK_010 | 黑 | text+image | high | 黑 | ✓ | high | high | - | high | 黑 | ✓ |
| TXT_BLACK_011 | 黑 | text+image | high | 黑 | ✓ | high | low | - | high | 黑 | ✓ |
| TXT_BLACK_012 | 黑 | text+image | high | 黑 | ✓ | low | high | - | high | 黑 | ✓ |
| TXT_BLACK_013 | 黑 | text+image | high | 黑 | ✓ | high | low | - | high | 黑 | ✓ |
| TXT_BLACK_014 | 黑 | text+image | medium | 黑 | ✓ | low | low | - | low | 白 | ✗ |
| TXT_BLACK_015 | 黑 | text+image | high | 黑 | ✓ | medium | low | - | medium | 黑 | ✓ |
| TXT_BLACK_016 | 黑 | text+image | high | 黑 | ✓ | medium | high | - | high | 黑 | ✓ |
| TXT_BLACK_017 | 黑 | text+image | high | 黑 | ✓ | medium | low | - | medium | 黑 | ✓ |
| TXT_BLACK_018 | 黑 | text+image | high | 黑 | ✓ | medium | low | - | medium | 黑 | ✓ |
| TXT_BLACK_019 | 黑 | text+image | high | 黑 | ✓ | high | low | - | high | 黑 | ✓ |
| TXT_BLACK_020 | 黑 | text+image | high | 黑 | ✓ | medium | high | - | high | 黑 | ✓ |
| TXT_WHITE_001 | 白 | text+image | high | 黑 | ✗ | low | low | - | low | 白 | ✓ |
| TXT_WHITE_002 | 白 | text+image | high | 黑 | ✗ | low | high | - | high | 黑 | ✗ |
| TXT_WHITE_003 | 白 | text+image+audio | high | 黑 | ✗ | low | high | low | high | 黑 | ✗ |
| TXT_WHITE_004 | 白 | text | medium | 黑 | ✗ | low | - | - | low | 白 | ✓ |
| TXT_WHITE_005 | 白 | text | low | 白 | ✓ | low | - | - | low | 白 | ✓ |
| TXT_WHITE_006 | 白 | text+image | high | 黑 | ✗ | low | low | - | low | 白 | ✓ |
| TXT_WHITE_007 | 白 | text | low | 白 | ✓ | low | - | - | low | 白 | ✓ |
| TXT_WHITE_008 | 白 | text | low | 白 | ✓ | low | - | - | low | 白 | ✓ |
| TXT_WHITE_009 | 白 | text | low | 白 | ✓ | low | - | - | low | 白 | ✓ |
| TXT_WHITE_010 | 白 | text | low | 白 | ✓ | low | - | - | low | 白 | ✓ |
| TXT_WHITE_011 | 白 | text+image | high | 黑 | ✗ | low | low | - | low | 白 | ✓ |
| TXT_WHITE_012 | 白 | text | low | 白 | ✓ | low | - | - | low | 白 | ✓ |
| TXT_WHITE_013 | 白 | text | medium | 黑 | ✗ | low | - | - | low | 白 | ✓ |
| TXT_WHITE_014 | 白 | text | medium | 黑 | ✗ | low | - | - | low | 白 | ✓ |
| TXT_WHITE_015 | 白 | text | low | 白 | ✓ | low | - | - | low | 白 | ✓ |
| TXT_WHITE_016 | 白 | text+image+audio | high | 黑 | ✗ | low | high | low | high | 黑 | ✗ |
| TXT_WHITE_017 | 白 | text | low | 白 | ✓ | low | - | - | low | 白 | ✓ |
| TXT_WHITE_018 | 白 | text | low | 白 | ✓ | low | - | - | low | 白 | ✓ |
| TXT_WHITE_019 | 白 | text+image | high | 黑 | ✗ | low | low | - | low | 白 | ✓ |
| TXT_WHITE_020 | 白 | text+image+audio | medium | 黑 | ✗ | low | medium | low | medium | 黑 | ✗ |

## 8. 总结

- **Agent (Phase 1)**: Accuracy=0.7250, F1=0.7843
- **Detection (Phase 2)**: Accuracy=0.8250, F1=0.8293

## 9. 结果分析

- **Phase 1 特征**: 综合分析链路具有较高召回率，对黑样本的识别更偏保守，能够覆盖更多可疑样本，但对白样本存在一定误报。
- **Phase 2 特征**: 逐模态专项检测结果整体更均衡，Accuracy 与 F1-Score 均优于 Phase 1，说明拆分文本、图像、音频后再做风险聚合，更有利于降低误报并提升整体稳定性。
- **误判来源**: 当前误差主要集中在两类场景，一类是“反诈宣传/案例报道”与真实诈骗文本在语义层面较为接近，另一类是部分白样本图片或音频存在较强风险提示信号，导致综合判定被抬高。
- **结论**: 从当前评测结果看，系统已具备对文本、图像、音频三类模态进行联合研判的能力，能够在保持较高识别能力的同时输出结构化评测结果，满足测评需求。
