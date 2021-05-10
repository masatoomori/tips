## スクリプトを非表示にする

```python
from IPython.display import HTML

HTML("""
<button id="code-show-switch-btn">スクリプトを非表示にする</button>

<script>
var code_show = true;

function switch_display_setting() {
    var switch_btn = $("#code-show-switch-btn");
    if (code_show) {
        $("div.input").hide();
        code_show = false;
        switch_btn.text("スクリプトを表示する");
    }else {
        $("div.input").show();
        code_show = true;
        switch_btn.text("スクリプトを非表示にする");
    }
}

$("#code-show-switch-btn").click(switch_display_setting);
</script>
""")
```

## 表示幅を変更する

```html
%%HTML
<style>
    div#notebook-container    { width: 95%; }
    div#menubar-container     { width:95%; }
    div#maintoolbar-container { width: 95%; }
</style>
```