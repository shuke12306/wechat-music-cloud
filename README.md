# 节点纯净度优选

这是一个本地自动化工具，用来批量测试 Clash Verge 节点的出口 IP 纯净度，并把每个地区里欺诈分最低的节点同步到两个目标：

- `shuke.yaml`：供 Clash Verge 导入使用
- GitHub Gist 订阅：供手机端等客户端更新订阅

当前项目已精简为一个主程序 `node_purity_tool.py`，配一个双击入口 `一键优选.bat`。

## 整体流程

```text
config(1).yaml
      |
      v
node_purity_tool.py test
      |
      v
节点测试结果.json
      |
      +--> node_purity_tool.py update-shuke --> shuke.yaml
      |
      +--> node_purity_tool.py update-gist  --> GitHub Gist 订阅
```

完整一键流程是：

1. 读取 `config(1).yaml` 里的节点。
2. 通过 Clash 外部控制器逐个切换节点。
3. 走 Clash 代理访问 IPPure，取得出口 IP、欺诈分、ISP、ASN、住宅/机房、地理位置。
4. 把全部测试结果写入 `节点测试结果.json`。
5. 询问是否把各地区最低风险节点写入 `shuke.yaml`。
6. 询问是否把各地区最低风险节点生成 vless 链接并写入 GitHub Gist。

## 快速使用

推荐直接双击：

```text
一键优选.bat
```

它等价于：

```bash
python node_purity_tool.py all
```

`all` 会先跑节点测试，然后分别询问：

- 是否更新 `shuke.yaml`
- 是否更新 GitHub Gist 订阅

测试结果 `节点测试结果.json` 在第一步就会写入；后面无论选不选择更新 `shuke.yaml` 或 Gist，都不影响测试结果保存。

## 手动命令

### 完整流程

```bash
python node_purity_tool.py all
```

### 只测试节点

```bash
python node_purity_tool.py test
```

这一步会真实连接 Clash Verge、切换节点、访问 IPPure，并覆盖写入 `节点测试结果.json`。

### 只更新 shuke.yaml

```bash
python node_purity_tool.py update-shuke
```

这一步不会重新测试节点，只读取已有的 `节点测试结果.json`。

程序会先打印更新预览，包括：

- 将删除哪些旧的 `优选-` 节点
- 将写入哪些新节点
- 每个新节点来自哪个地区、欺诈分是多少
- 新节点会加入哪个代理组

确认无误后输入 `Y` 才会写入 `shuke.yaml`。

### 只更新 Gist 订阅

```bash
python node_purity_tool.py update-gist
```

这一步不会重新测试节点，只读取已有的 `节点测试结果.json`。

程序会：

1. 选出香港、台湾、日本、新加坡各自最低风险节点。
2. 从 `config(1).yaml` 读取这些节点的完整配置。
3. 生成 vless 链接。
4. 拉取 Gist 当前内容。
5. 打印更新预览。
6. 输入 `Y` 后才 PATCH 写入 Gist。

## 预览模式

### 预览 shuke.yaml 更新

```bash
python node_purity_tool.py update-shuke --dry-run
```

只打印将要修改的内容，不写 `shuke.yaml`。

### 预览 Gist 更新

```bash
python node_purity_tool.py update-gist --dry-run
```

会真实拉取 Gist 当前内容，用来生成准确预览；但不会写入 Gist，也不会要求确认。

### 完整流程中的预览

```bash
python node_purity_tool.py all --dry-run
```

注意：`all --dry-run` 中，第一步 `test` 仍会真实测试节点并写入 `节点测试结果.json`。`--dry-run` 只影响后续 `update-shuke` 和 `update-gist`，让它们只预览不写入。

## 日志与排查

默认只显示正常运行输出，不生成日志文件。

显示详细请求和重试信息：

```bash
python node_purity_tool.py all --verbose
```

写入日志文件：

```bash
python node_purity_tool.py all --log-file node_purity.log
```

可以同时使用：

```bash
python node_purity_tool.py all --verbose --log-file node_purity.log
```

网络请求统一带有限重试。会重试：

- 超时
- 连接错误
- HTTP 429
- HTTP 500 / 502 / 503 / 504

不会盲目重试明显的配置或权限错误，例如 401、403、404。

## 前提条件

### Python 依赖

```bash
pip install requests pyyaml ruamel.yaml
```

`requests` 用于访问 Clash、IPPure、GitHub API。

`pyyaml` 用于读取 `config(1).yaml`。

`ruamel.yaml` 用于写入 `shuke.yaml`，它能保留 YAML 注释和格式。

### Clash Verge 设置

脚本按当前机器环境写死了这些值：

| 项目 | 当前值 |
|------|--------|
| 代理端口 | `7897` |
| 外部控制器 | `127.0.0.1:9091` |
| API 密钥 | `Echo-9Purple_Matrix-7Flight` |
| 选择组 | `🚀 节点选择` |

Clash Verge 里必须开启外部控制器，并且监听地址、密钥要和脚本一致。

如果这些值变化，需要修改 `node_purity_tool.py` 顶部常量：

- `CLASH_API`
- `CLASH_SECRET`
- `HTTP_PROXY`
- `SELECT_GROUP`

## 文件说明

| 文件 | 作用 |
|------|------|
| `node_purity_tool.py` | 主程序，包含测试、选优、写入 `shuke.yaml`、更新 Gist |
| `一键优选.bat` | Windows 双击入口，调用 `python node_purity_tool.py all` |
| `config(1).yaml` | 节点源配置，脚本从这里读取完整节点信息 |
| `shuke.yaml` | 输出目标，供 Clash Verge 导入 |
| `节点测试结果.json` | 节点测试结果，后续选优步骤读取它 |
| `gist_config.json` | GitHub Gist 配置，包含 token、gist_id、filename |

`gist_config.json` 含 GitHub token，能修改你的 Gist。不要发给别人，不要上传到公开位置。

## 节点测试逻辑

`test` 命令的核心逻辑：

1. 读取 `config(1).yaml` 的 `proxies`。
2. 只筛选目标地区：
   - 香港
   - 美国
   - 台湾
   - 日本
   - 新加坡
3. 对每个节点：
   - 调用 Clash API 读取代理组。
   - 确认节点存在于可手动切换的 Selector 组。
   - 把 `🚀 节点选择` 切换到目标节点。
   - 回读 `now` 字段确认切换真的生效。
   - 通过 `7897` 代理访问 `https://my.ippure.com/v1/info`。
   - 记录出口 IP、欺诈分、ISP、ASN、类型、地理位置。
4. 测试完成后排序并写入 `节点测试结果.json`。

IPPure 返回的是 JSON，比爬网页稳定。脚本只把合法 JSON 且含 `ip` 字段的响应当成有效结果，避免把限流页或异常页误判成真实 0 分。

## 测试结果结构

新的 `节点测试结果.json` 是三段式：

```json
{
  "top10_lowest_risk": [],
  "by_region": {},
  "all_ranked": []
}
```

含义：

| 字段 | 含义 |
|------|------|
| `top10_lowest_risk` | 全局欺诈分最低的前 10 个节点 |
| `by_region` | 按地区分组，每组内按欺诈分排序 |
| `all_ranked` | 全部节点按欺诈分排序，失败或无分的排后面 |

后续命令仍兼容旧的扁平数组格式，所以旧结果文件也能继续用。

风险分级：

| 欺诈分 | 分级 |
|--------|------|
| 0-25 | 低风险 |
| 26-50 | 中风险 |
| 51-75 | 高风险 |
| 76-100 | 极高风险 |

## 写入 shuke.yaml 的逻辑

`update-shuke` 默认只处理：

- 香港
- 台湾
- 日本
- 新加坡

美国逻辑已保留，但默认关闭：`INCLUDE_US = False`。

选优规则：

1. 读取 `节点测试结果.json`。
2. 每个地区只选欺诈分最低的一个节点。
3. 根据节点名回到 `config(1).yaml` 找完整节点配置。
4. 给新节点名加 `优选-` 前缀。
5. 删除 `shuke.yaml` 里旧的 `优选-` 节点。
6. 写入新的优选节点。
7. 把港、台、日、新的优选节点加入 `日本(其他)` 组。

为什么加 `优选-`：

`shuke.yaml` 里可能已经有同名节点，例如另一台服务器的 `日本 01`。直接写入同名节点会造成配置混乱。`优选-` 既能防撞名，也让重复运行时可以精确清理上一次导入的节点。

写入前一定会打印预览。非 dry-run 时，输入 `Y` 才会真正写入。

## 更新 Gist 的逻辑

`update-gist` 默认只为香港、台湾、日本、新加坡生成链接。

vless 链接格式复刻当前客户端使用的 Shadowrocket 风格：

```text
vless://base64(auto:{uuid}@{server}:{port})?remarks={name}&tls=1&peer={servername}&allowInsecure=1&udp=1&xtls=2
```

Gist 更新策略：

1. 保留固定节点：
   - `日本01`
   - `美国09`
2. 加入本次各地区最低风险节点。
3. 删除其他旧节点。
4. 所有节点 remarks 统一去空格。

保留固定节点时按备注名匹配，不按服务器地址匹配。原因是部分节点可能共用同一台服务器，仅靠地址无法区分。

如果某个最优节点是 reality 节点，脚本会跳过生成链接。当前简化 vless URI 无法完整表达 reality 的 `public-key` / `short-id` 等参数，强行生成容易得到坏链接。

## 安全与回滚

这个工具现在不再自动生成：

- `shuke.yaml.bak`
- `gist_backup.txt`

这是为了保持文件夹精简。

回滚方式：

- `shuke.yaml`：使用 Clash Verge 自身配置备份、历史文件，或你手动保留的副本。
- Gist：使用 GitHub Gist 的历史记录回滚。

建议在确认大改之前先跑：

```bash
python node_purity_tool.py update-shuke --dry-run
python node_purity_tool.py update-gist --dry-run
```

## 常见问题

### API 连不上

检查 Clash Verge 是否开启外部控制器。

监听地址应为：

```text
127.0.0.1:9091
```

API 密钥必须和脚本里的 `CLASH_SECRET` 一致。

### 代理出网失败

检查 Clash Verge 代理端口是否是：

```text
7897
```

还要确认当前网络能正常访问国外网站。

### 找不到选择组

脚本默认选择组是：

```text
🚀 节点选择
```

如果你的配置里组名变了，需要修改 `SELECT_GROUP`。

### IPPure 查询失败

可能原因：

- IPPure 临时不可用
- 当前节点访问失败
- 请求被限流
- 返回异常内容

脚本会重试 429 和 5xx。持续失败时，可以稍后再跑，或用 `--verbose` 查看更详细日志。

### update-shuke 没写入

确认是否只用了 `--dry-run`。

正常写入需要在预览后输入 `Y`。

### update-gist 没写入

确认：

- `gist_config.json` 里 token 有效
- token 是 classic token，并勾选 `gist` 权限
- `gist_id` 和 `filename` 正确
- 没有使用 `--dry-run`
- 预览后输入了 `Y`

### 文件夹又出现 __pycache__

这是 Python 导入脚本时自动生成的字节码缓存。它不是项目必需文件，可以删除。删除后下次导入或编译可能再次生成。

## 推荐使用习惯

日常直接双击：

```text
一键优选.bat
```

不确定会改什么时，先跑：

```bash
python node_purity_tool.py update-shuke --dry-run
python node_purity_tool.py update-gist --dry-run
```

排查问题时：

```bash
python node_purity_tool.py all --verbose
```

需要保存排查记录时：

```bash
python node_purity_tool.py all --verbose --log-file node_purity.log
```
