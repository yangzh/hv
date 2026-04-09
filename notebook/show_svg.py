"""SVG viewer helper for Jupyter notebooks."""

import uuid

from IPython.display import HTML, display

_JS = """
function initSvgViewer(cid, containerW, containerH, miniSize, panStep) {
    var c = document.getElementById(cid), inner = c.firstElementChild;
    var zoomLabel = document.getElementById(cid + "-zoom");
    var miniSvg = document.getElementById(cid + "-mini-svg");
    var vp = document.getElementById(cid + "-vp");

    var svgEl = inner.querySelector("svg");
    var svgW = svgEl ? parseFloat(svgEl.getAttribute("width")) || containerW : containerW;
    var svgH = svgEl ? parseFloat(svgEl.getAttribute("height")) || containerH : containerH;

    var fitScale = Math.min(containerW / svgW, containerH / svgH);
    var s = 1, px = 0, py = 0, drag = false, sx, sy;

    // Prevent browser from auto-scaling SVG to fit container.
    if (svgEl) {
        svgEl.style.width = svgW + "px";
        svgEl.style.height = svgH + "px";
        svgEl.style.maxWidth = "none";
        inner.style.width = svgW + "px";
        inner.style.height = svgH + "px";

        var clone = svgEl.cloneNode(true);
        clone.style.width = miniSize + "px";
        clone.style.height = miniSize + "px";
        clone.setAttribute("width", miniSize);
        clone.setAttribute("height", miniSize);
        miniSvg.appendChild(clone);
    }

    function update() {
        inner.style.transform = "translate(" + px + "px," + py + "px) scale(" + s + ")";
        zoomLabel.textContent = Math.round((s / fitScale) * 100) + "%";
        var miniScaleX = miniSize / svgW, miniScaleY = miniSize / svgH;
        var vpW = Math.min(miniSize, (containerW / s) * miniScaleX);
        var vpH = Math.min(miniSize, (containerH / s) * miniScaleY);
        vp.style.width = vpW + "px";
        vp.style.height = vpH + "px";
        vp.style.left = Math.max(0, Math.min(miniSize - vpW, (-px / s) * miniScaleX)) + "px";
        vp.style.top = Math.max(0, Math.min(miniSize - vpH, (-py / s) * miniScaleY)) + "px";
    }
    update();

    document.getElementById(cid + "-reset").onclick = function() { s = 1; px = 0; py = 0; update(); };
    var zoomStep = fitScale * 0.25;
    document.getElementById(cid + "-zi").onclick = function() { s += zoomStep; update(); };
    document.getElementById(cid + "-zo").onclick = function() { s = Math.max(zoomStep, s - zoomStep); update(); };
    document.getElementById(cid + "-up").onclick = function() { py += panStep; update(); };
    document.getElementById(cid + "-down").onclick = function() { py -= panStep; update(); };
    document.getElementById(cid + "-left").onclick = function() { px += panStep; update(); };
    document.getElementById(cid + "-right").onclick = function() { px -= panStep; update(); };
    c.onwheel = function(e) { e.preventDefault(); s *= e.deltaY > 0 ? 0.9 : 1.1; update(); };
    c.onmousedown = function(e) { drag = true; sx = e.clientX - px; sy = e.clientY - py; c.style.cursor = "grabbing"; };
    c.onmousemove = function(e) { if (drag) { px = e.clientX - sx; py = e.clientY - sy; update(); } };
    c.onmouseup = c.onmouseleave = function() { drag = false; c.style.cursor = "grab"; };
}
"""

# Inject JS once on import.
display(HTML(f"<script>{_JS}</script>"))


def show_svg(svg_str, width=600, height=600):
    """Display an SVG with zoom/pan controls, minimap, and direction buttons."""
    cid = f"svg-{uuid.uuid4().hex[:8]}"
    mini_size = 120
    pan_step = 50
    return HTML(f'''
    <div style="display:flex; gap:10px; align-items:flex-start;">
        <div id="{cid}" style="width:{width}px; height:{height}px; overflow:hidden; border:1px solid #ccc; cursor:grab;">
            <div style="transform-origin:0 0; display:inline-block;">{svg_str}</div>
        </div>
        <div style="display:flex; flex-direction:column; gap:6px; font:11px monospace; color:#666;">
            <div>overview</div>
            <div id="{cid}-mini" style="width:{mini_size}px; height:{mini_size}px; border:1px solid #999; background:#fff; position:relative; overflow:hidden;">
                <div id="{cid}-mini-svg" style="transform-origin:0 0;"></div>
                <div id="{cid}-vp" style="position:absolute; border:2px solid red;"></div>
            </div>
            <div>zoom</div>
            <div id="{cid}-zoom" style="text-align:center;">100%</div>
            <div style="display:flex; gap:4px; justify-content:center;">
                <button id="{cid}-zi" style="font:12px monospace; width:28px; cursor:pointer;">+</button>
                <button id="{cid}-zo" style="font:12px monospace; width:28px; cursor:pointer;">&minus;</button>
                <button id="{cid}-reset" style="font:10px monospace; padding:1px 6px; cursor:pointer;">Reset</button>
            </div>
            <div style="margin-top:4px;">pan</div>
            <div style="display:grid; grid-template-columns:28px 28px 28px; grid-template-rows:28px 28px 28px; gap:2px; justify-content:center;">
                <div></div>
                <button id="{cid}-up" style="font:12px monospace; width:28px; cursor:pointer;">&uarr;</button>
                <div></div>
                <button id="{cid}-left" style="font:12px monospace; width:28px; cursor:pointer;">&larr;</button>
                <div></div>
                <button id="{cid}-right" style="font:12px monospace; width:28px; cursor:pointer;">&rarr;</button>
                <div></div>
                <button id="{cid}-down" style="font:12px monospace; width:28px; cursor:pointer;">&darr;</button>
                <div></div>
            </div>
        </div>
    </div>
    <script>initSvgViewer("{cid}", {width}, {height}, {mini_size}, {pan_step});</script>
    ''')
