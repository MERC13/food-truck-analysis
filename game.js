Qualtrics.SurveyEngine.addOnload(function() {
  var q = this;
  q.hideNextButton();

  var root = document.getElementById("bobalab-root");
  if (!root) {
    root = document.createElement("div");
    root.id = "bobalab-root";
    this.getQuestionContainer().appendChild(root);
  }
  root.innerHTML = "";
  root.style.maxWidth = "1100px";
  root.style.margin = "0 auto";
  root.style.padding = "0";

  // ─── STYLES ───────────────────────────────────────────────────────────────
  var style = document.createElement("style");
  style.type = "text/css";
  style.textContent = `
#bobalab-root {
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
  color: #0f172a;
}
#bobalab-root main {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 0 12px 16px;
}
#bobalab-root .flexbox-container {
  display: flex;
  flex-grow: 1;
  overflow: hidden;
  gap: 14px;
}
#bobalab-root #bobalab-app { width: 100%; }

/* ── Banner ── */
#bobalab-root #main-banner {
  height: auto;
  min-height: 120px;
  border-radius: 18px;
  margin: 14px 12px 18px;
  padding: 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, rgba(16,185,129,0.22), rgba(34,54,34,0.55));
  box-shadow: 0 10px 30px rgba(15,23,42,0.14);
  color: #0f172a;
}
#bobalab-root #profit-indicator,
#bobalab-root #park-status,
#bobalab-root #time-indicator { padding: 12px 14px; flex: 1; }
#bobalab-root #profit-indicator strong,
#bobalab-root #time-indicator strong { font-size: 15px; color: #0f172a; }
#bobalab-root #profit-gains {
  margin-top: 8px; padding: 8px 10px;
  display: inline-block; border-radius: 999px;
  background: rgba(16,185,129,0.14); color: #064e3b; font-weight: 700;
}
#bobalab-root #park-status {
  text-align: center; border: none;
  background: rgba(255,255,255,0.82);
  border-radius: 16px; box-shadow: 0 6px 16px rgba(15,23,42,0.10);
}
#bobalab-root #current-park { margin: 0 0 6px 0; font-size: 20px; letter-spacing: 0.2px; }
#bobalab-root #hint { color: #4f46e5; font-weight: 700; font-size: 13px; margin: 4px 0 0; }
#bobalab-root #expected-profit-display {
  margin: 4px 0 2px; font-size: 13px; font-weight: 700;
  color: #065f46; background: rgba(16,185,129,0.18);
  border-radius: 8px; padding: 4px 10px; display: inline-block;
}

/* ── Panels ── */
#bobalab-root #history-container {
  width: 30%; height: 75vh; overflow-y: auto;
  padding: 14px 14px 10px; border: none;
  background: rgba(255,255,255,0.88);
  border-radius: 18px; box-shadow: 0 10px 30px rgba(15,23,42,0.10);
}
#bobalab-root #history-container h2 { margin: 0 0 10px; font-size: 16px; letter-spacing: 0.2px; }
#bobalab-root #history-container ul { margin: 0; padding-left: 18px; font-size: 14px; line-height: 1.35; }
#bobalab-root #history-container li { margin-bottom: 6px; }

#bobalab-root #map {
  width: 70%; background: rgba(255,255,255,0.50);
  border-radius: 18px; padding: 14px;
  box-shadow: 0 10px 30px rgba(15,23,42,0.08);
  display: flex; flex-direction: column;
}
#bobalab-root #map h2 { margin: 4px 0 12px; font-size: 16px; color: #0f172a; }

/* ── Observation panel ── */
#bobalab-root #observation-text-container {
  background: rgba(15,23,42,0.05);
  border: 1px solid rgba(15,23,42,0.08);
  border-radius: 14px; padding: 10px 12px; margin-bottom: 12px;
}
#bobalab-root #observation-text-container p { margin: 6px 0; font-size: 14px; }

/* ── Tip rating panel ── */
#bobalab-root #tip-rating-container {
  background: linear-gradient(135deg, rgba(79,70,229,0.07), rgba(79,70,229,0.13));
  border: 1px solid rgba(79,70,229,0.18);
  border-radius: 14px; padding: 14px 16px; margin-bottom: 12px;
  display: flex; flex-direction: column; gap: 10px;
}
#bobalab-root #tip-rating-container p {
  margin: 0; font-size: 14px; font-weight: 600; color: #3730a3;
}
#bobalab-root #tip-rating-container .tip-text {
  font-size: 14px; color: #1e1b4b; font-weight: 400;
  background: rgba(255,255,255,0.6); border-radius: 8px;
  padding: 8px 10px; margin: 0;
}
#bobalab-root #tip-rating-buttons {
  display: flex; gap: 10px; align-items: center;
}
#bobalab-root .tip-rate-btn {
  background: rgba(255,255,255,0.8);
  border: 1px solid rgba(79,70,229,0.25);
  border-radius: 10px; padding: 8px 14px;
  font-size: 18px; cursor: pointer;
  transition: transform 100ms ease, background 100ms ease, border-color 100ms ease;
  line-height: 1;
}
#bobalab-root .tip-rate-btn:hover {
  transform: scale(1.12);
  background: rgba(255,255,255,1);
  border-color: rgba(79,70,229,0.5);
}
#bobalab-root .tip-rate-btn.rated {
  opacity: 0.45; transform: none; cursor: default; pointer-events: none;
}
#bobalab-root .tip-rate-btn.chosen {
  opacity: 1; background: rgba(79,70,229,0.12);
  border-color: rgba(79,70,229,0.55);
}
#bobalab-root #tip-rated-label {
  font-size: 12px; color: #6366f1; font-style: italic;
}

/* ── Buttons ── */
#bobalab-root #button-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 14px; max-width: 860px; width: 100%;
  padding: 8px 0 12px; box-sizing: border-box;
}
#bobalab-root .park-button {
  color: white; padding: 16px; font-size: 15px;
  border: none; border-radius: 16px; cursor: pointer;
  text-align: center; font-weight: 800; letter-spacing: 0.2px;
  transition: transform 120ms ease, box-shadow 120ms ease, filter 120ms ease; margin: 0;
}
#bobalab-root .park-button:hover { transform: translateY(-3px); filter: brightness(1.08); }

/* Per-park colors */
#bobalab-root .park-button.park-color-0 {
  background: linear-gradient(160deg, #10b981, #065f46);
  box-shadow: 0 10px 18px rgba(16,185,129,0.35);
}
#bobalab-root .park-button.park-color-1 {
  background: linear-gradient(160deg, #3b82f6, #1e3a8a);
  box-shadow: 0 10px 18px rgba(59,130,246,0.35);
}
#bobalab-root .park-button.park-color-2 {
  background: linear-gradient(160deg, #f59e0b, #92400e);
  box-shadow: 0 10px 18px rgba(245,158,11,0.35);
}
#bobalab-root .park-button.park-color-3 {
  background: linear-gradient(160deg, #ec4899, #831843);
  box-shadow: 0 10px 18px rgba(236,72,153,0.35);
}
#bobalab-root .park-button.park-color-4 {
  background: linear-gradient(160deg, #8b5cf6, #4c1d95);
  box-shadow: 0 10px 18px rgba(139,92,246,0.35);
}
#bobalab-root .park-button.park-color-5 {
  background: linear-gradient(160deg, #ef4444, #7f1d1d);
  box-shadow: 0 10px 18px rgba(239,68,68,0.35);
}
#bobalab-root .park-icon {
  vertical-align: middle; margin-left: 10px;
  width: 34px; height: 34px; opacity: 0.95;
  display: inline-block; background-size: contain; background-repeat: no-repeat;
}
#bobalab-root #minigame-start-button {
  background: linear-gradient(180deg, rgba(59,130,246,0.95), rgba(37,99,235,0.95));
  color: white; padding: 16px 18px; font-size: 16px;
  border: none; border-radius: 16px; cursor: pointer;
  text-align: center; font-weight: 800; letter-spacing: 0.2px;
  box-shadow: 0 10px 18px rgba(37,99,235,0.25);
  transition: transform 120ms ease, filter 120ms ease; margin: 10px 0;
}
#bobalab-root #minigame-start-button:hover { transform: translateY(-2px); filter: brightness(1.04); }

#bobalab-root #continue-button {
  background: linear-gradient(180deg, rgba(245,158,11,0.95), rgba(217,119,6,0.95));
  color: white; padding: 14px 18px; font-size: 16px;
  margin: 14px auto 0; display: block; border: none;
  cursor: pointer; border-radius: 16px; font-weight: 800;
  box-shadow: 0 10px 18px rgba(217,119,6,0.22);
  transition: transform 120ms ease, filter 120ms ease;
}
#bobalab-root #continue-button:hover { transform: translateY(-2px); filter: brightness(1.04); }

/* ── Utility ── */
#bobalab-root .no-display { display: none !important; }

/* ── Memory game ── */
#bobalab-root #sequence-display {
  display: flex; align-items: center; justify-content: center;
  background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.12);
  border-radius: 18px; padding: 18px; margin-bottom: 18px;
  box-shadow: 0 18px 50px rgba(0,0,0,0.35);
}
#bobalab-root #sequence-display .sequence-item {
  width: 120px; height: 120px; margin: 0;
  filter: drop-shadow(0 10px 18px rgba(0,0,0,0.28));
}
#bobalab-root #input-container {
  display: flex; flex-wrap: wrap; justify-content: center;
  gap: 12px; max-width: 720px; padding: 10px;
}
#bobalab-root #input-container .input-button {
  border-radius: 16px; border: 1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.08); padding: 12px; margin: 0;
  cursor: pointer; outline: none;
  transition: transform 120ms ease, background 120ms ease, border-color 120ms ease, opacity 120ms ease;
}
#bobalab-root #input-container .input-button:hover {
  transform: translateY(-1px); background: rgba(255,255,255,0.11);
  border-color: rgba(255,255,255,0.20);
}
#bobalab-root #input-container .input-button.selected {
  opacity: 0.55; transform: none; border-color: rgba(96,165,250,0.35);
}
#bobalab-root #input-container .input-item {
  width: 86px; height: 86px;
  filter: drop-shadow(0 10px 16px rgba(0,0,0,0.22));
}

/* ── Profit preview panel ── */
#bobalab-root #profit-preview-container {
  background: linear-gradient(135deg, rgba(16,185,129,0.08), rgba(5,150,105,0.15));
  border: 1px solid rgba(16,185,129,0.28);
  border-radius: 14px; padding: 12px 16px; margin-bottom: 12px;
  display: flex; flex-direction: column; gap: 6px;
}
#bobalab-root #profit-preview-container .preview-label {
  font-size: 13px; font-weight: 700; color: #065f46; margin: 0; text-transform: uppercase; letter-spacing: 0.5px;
}
#bobalab-root #profit-preview-container .preview-stats {
  display: flex; gap: 16px; flex-wrap: wrap;
}
#bobalab-root #profit-preview-container .preview-stat {
  font-size: 14px; color: #0f172a; background: rgba(255,255,255,0.7);
  border-radius: 8px; padding: 5px 10px; font-weight: 600;
}
#bobalab-root #profit-preview-container .preview-range {
  font-size: 14px; color: #064e3b; font-weight: 700;
  background: rgba(16,185,129,0.18); border-radius: 8px; padding: 5px 10px;
}

/* ── Responsive ── */
@media (max-width: 900px) {
  #bobalab-root .flexbox-container { flex-direction: column; }
  #bobalab-root #history-container { width: 100%; height: 260px; }
  #bobalab-root #map { width: 100%; }
}
  `;
  document.head.appendChild(style);

  // ─── HTML SHELL ───────────────────────────────────────────────────────────
  root.innerHTML = `
    <div id="bobalab-app">
      <header id="main-banner">
        <div id="profit-indicator">
          <strong>Total Profits: $<span id="current-profit">0</span></strong>
          <p id="profit-gains" class="no-display">You gained $0!</p>
        </div>
        <div id="park-status">
          <h1 id="current-park">Home</h1>
          <p id="number-of-people"></p>
          <p id="number-of-food-trucks"></p>
          <p id="expected-profit-display" class="no-display"></p>
          <p id="hint"></p>
        </div>
        <div id="time-indicator">
          <strong>Day <span id="current-day">1</span> of <span id="final-day">5</span></strong>
          <br>
          <strong>Hour <span id="current-hour-display">1</span> of <span id="final-hour">1</span></strong>
        </div>
      </header>
      <main>
        <div class="flexbox-container">
          <div id="history-container"></div>
          <div id="map"></div>
        </div>
      </main>
    </div>
  `;

  // ─── UTILITIES ────────────────────────────────────────────────────────────
  function updateText(id, value) {
    var el = document.getElementById(id);
    if (el) el.textContent = value;
  }
  function hide(el) { if (el) el.classList.add("no-display"); }
  function show(el) { if (el) el.classList.remove("no-display"); }
  function randomInteger(lo, hi) {
    if (lo === undefined) lo = 1;
    if (hi < 0 || lo >= hi) return lo;
    return Math.floor(Math.random() * (hi - lo + 1)) + lo;
  }
  function svgToDataUri(svgText) {
    return "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svgText.replace(/\s+/g, " ").trim());
  }
  function getED(name, fallback) {
    try {
      var v = Qualtrics.SurveyEngine.getEmbeddedData(name);
      return (v === undefined || v === null || v === "") ? fallback : v;
    } catch(e) { return fallback; }
  }

  // ─── SVG ICONS ────────────────────────────────────────────────────────────
  var TACO_SVG = '<svg width="800px" height="800px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M13 4.5C13 4.67532 12.9699 4.84361 12.9146 5H13C13 4.17157 13.6716 3.5 14.5 3.5C15.3284 3.5 16 4.17157 16 5L15.9999 5.01446C16.1208 5.02147 16.2409 5.031 16.3603 5.043C16.5263 4.72055 16.8624 4.5 17.25 4.5C17.787 4.5 18.2251 4.92325 18.249 5.45435C21.5943 6.59707 24 9.7676 24 13.5V16C24 18.2091 22.2091 20 20 20H5.33333C2.38781 20 0 17.6122 0 14.6667V14C0 10.661 1.81827 7.74674 4.51866 6.19327C4.50642 6.13074 4.5 6.06612 4.5 6C4.5 5.44772 4.94772 5 5.5 5C5.83151 5 6.12535 5.16132 6.30729 5.40973C6.5396 5.33699 6.77595 5.27341 7.01593 5.21942C7.00544 5.1478 7 5.07453 7 5C7 4.17157 7.67157 3.5 8.5 3.5C9.32843 3.5 10 4.17157 10 5H10.0854C10.0301 4.84361 10 4.67532 10 4.5C10 3.67157 10.6716 3 11.5 3C12.3284 3 13 3.67157 13 4.5ZM9 7C5.13401 7 2 10.134 2 14V14.6667C2 16.5076 3.49238 18 5.33333 18H16.5351C16.1948 17.4117 16 16.7286 16 16V13.6471C16 9.97599 13.024 7 9.35294 7H9ZM14.8839 7C16.7881 8.58616 18 10.9751 18 13.6471V15V16C18 17.1046 18.8954 18 20 18C21.1046 18 22 17.1046 22 16V13.5C22 13.3749 21.9965 13.2507 21.9895 13.1274C21.7254 13.3593 21.3791 13.5 21 13.5C20.1716 13.5 19.5 12.8284 19.5 12C19.5 11.1716 20.1716 10.5 21 10.5C21.0962 10.5 21.1903 10.5091 21.2815 10.5264C20.9459 9.87521 20.5035 9.28807 19.9775 8.78808C19.9922 8.85638 20 8.92729 20 9C20 9.55228 19.5523 10 19 10C18.4477 10 18 9.55228 18 9C18 8.45891 18.4298 8.01819 18.9666 8.00055C17.9632 7.36678 16.7745 7 15.5 7H14.8839ZM18 15C18 14.4477 18.4477 14 19 14C19.5523 14 20 14.4477 20 15C20 15.5523 19.5523 16 19 16C18.4477 16 18 15.5523 18 15Z" fill="#000000"/></svg>';
  var BURGER_SVG = '<svg width="800px" height="800px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M5 10C5 7.23858 7.23858 5 10 5H14C16.7614 5 19 7.23858 19 10V10.8382C17.9457 9.59948 16.026 9.60669 14.9818 10.8598C14.7311 11.1607 14.2689 11.1607 14.0182 10.8598C12.9679 9.59944 11.0321 9.59944 9.98178 10.8598C9.73105 11.1607 9.26895 11.1607 9.01822 10.8598C7.97395 9.60669 6.05435 9.59948 5 10.8382V10ZM21 10V10.5C21.2559 10.5 21.5118 10.5976 21.7071 10.7929C22.0976 11.1834 22.0976 11.8166 21.7071 12.2071L21.5246 12.3896C21.1544 12.7599 20.7056 12.999 20.234 13.1095C21.2565 13.4231 22 14.3747 22 15.5C22 16.3607 21.565 17.1199 20.9029 17.5696C20.9651 17.6999 21 17.8459 21 18V18.5C21 20.433 19.433 22 17.5 22H6.5C4.567 22 3 20.433 3 18.5V18C3 17.8459 3.03486 17.6999 3.09712 17.5696C2.43498 17.1199 2 16.3607 2 15.5C2 14.3747 2.74348 13.4231 3.76602 13.1095C3.29437 12.999 2.84564 12.7599 2.47537 12.3896L2.29289 12.2071C1.90237 11.8166 1.90237 11.1834 2.29289 10.7929C2.48816 10.5976 2.74408 10.5 3 10.5V10C3 6.13401 6.13401 3 10 3H14C17.866 3 21 6.13401 21 10ZM5.35966 13H8.83259C8.32453 12.8675 7.84903 12.5809 7.48178 12.1402C7.23105 11.8393 6.76895 11.8393 6.51822 12.1402L6.46105 12.2088C6.15489 12.5762 5.77366 12.8406 5.35966 13ZM10.1674 13H13.8326C13.3245 12.8675 12.849 12.5809 12.4818 12.1402C12.2311 11.8393 11.7689 11.8393 11.5182 12.1402C11.151 12.5809 10.6755 12.8675 10.1674 13ZM15.1674 13H18.6403C18.2263 12.8406 17.8451 12.5762 17.5389 12.2088L17.4818 12.1402C17.2311 11.8393 16.7689 11.8393 16.5182 12.1402C16.151 12.5809 15.6755 12.8675 15.1674 13ZM5 18V18.5C5 19.3284 5.67157 20 6.5 20H17.5C18.3284 20 19 19.3284 19 18.5V18H5ZM4 15.5C4 15.2239 4.22386 15 4.5 15H19.5C19.7761 15 20 15.2239 20 15.5C20 15.7761 19.7761 16 19.5 16H4.5C4.22386 16 4 15.7761 4 15.5Z" fill="#000000"/></svg>';
  var HOTDOG_SVG = '<svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M2.773,15.251a4.339,4.339,0,0,0,5.976,5.974,5.479,5.479,0,0,0,7.909.173L21.4,16.657a5.474,5.474,0,0,0,0-7.734h0l-.173-.173a4.339,4.339,0,0,0-5.976-5.974A5.479,5.479,0,0,0,7.342,2.6L2.6,7.343a5.475,5.475,0,0,0,0,7.735Zm17.213-.008-4.742,4.741a3.555,3.555,0,0,1-4.907,0l-.083-.083L19.9,10.254l.084.083A3.472,3.472,0,0,1,19.986,15.243ZM19.2,4.806a2.353,2.353,0,0,1,0,3.327L8.132,19.194a2.41,2.41,0,0,1-3.327,0,2.351,2.351,0,0,1,0-3.327L15.868,4.806a2.353,2.353,0,0,1,3.327,0ZM4.014,8.757,8.756,4.016a3.47,3.47,0,0,1,4.907,0l.083.083L4.1,13.746l-.084-.083A3.472,3.472,0,0,1,4.014,8.757ZM14.571,7.143h2.572a1,1,0,0,1,0,2H15.571c-.105.6.437,2.571-1,2.571H13v1.572a1,1,0,0,1-1,1H10.429v1.571c0,1.551-2.243.833-3.572,1a1,1,0,0,1,0-2H8.429V13.286c0-1.437,1.959-.894,2.571-1V10.714c0-1.437,1.959-.893,2.571-1C13.676,9.111,13.135,7.143,14.571,7.143Z"/></svg>';
  var PIZZA_SVG = '<svg width="800px" height="800px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M8.18092 2.56556C7.90392 3.05195 7.65396 3.65447 7.416 4.36507C5.57795 9.34447 2.73476 16.6246 1.36225 20.12C0.73894 21.7073 2.25721 23.2963 3.87117 22.7465C7.38796 21.5484 14.6626 19.0869 19.6353 17.5194L19.6504 17.5145C20.3639 17.277 20.9659 17.0333 21.4491 16.7641C21.9273 16.4977 22.3551 16.1704 22.6426 15.7347C23.2987 14.7406 22.9351 13.6998 22.5012 12.8954C19.7712 7.83439 16.3585 4.2775 12.0968 1.5703C11.6898 1.31179 11.2341 1.09226 10.7418 1.02286C10.2141 0.948472 9.69595 1.05467 9.22968 1.36307C8.79315 1.65181 8.45686 2.08103 8.18092 2.56556ZM15.0912 9.09151C13.5105 7.4048 11.7893 5.97947 9.55526 4.3325C9.6817 4.01505 9.80284 3.75901 9.91885 3.55532C10.1115 3.21703 10.2575 3.08115 10.333 3.03119C10.3788 3.0009 10.4025 2.99481 10.4626 3.00327C10.5579 3.01672 10.7358 3.07517 11.0244 3.25848C14.994 5.78016 18.1714 9.08132 20.741 13.8449C21.0989 14.5085 20.9833 14.6233 20.9739 14.6325L20.9734 14.6331C20.9318 14.696 20.8089 14.8313 20.4757 15.017C20.2861 15.1226 20.0491 15.2333 19.7558 15.3501C18.0975 12.7134 16.6772 10.7839 15.0912 9.09151ZM13.6318 10.4591C15.0211 11.9415 16.2981 13.6452 17.8022 16.0033C12.9009 17.5716 6.46194 19.751 3.22621 20.8533L3.22459 20.8538L3.22391 20.8531L3.22329 20.8525L3.22387 20.851C4.48689 17.6345 7.00299 11.1934 8.83498 6.28876C10.7878 7.75003 12.2738 9.00998 13.6318 10.4591ZM10 13C11.1046 13 12 12.1046 12 11C12 9.89545 11.1046 9.00002 10 9.00002C8.89543 9.00002 8 9.89545 8 11C8 12.1046 8.89543 13 10 13ZM10 16C10 17.1046 9.10457 18 8 18C6.89543 18 6 17.1046 6 16C6 14.8954 6.89543 14 8 14C9.10457 14 10 14.8954 10 16ZM13 17C14.1046 17 15 16.1046 15 15C15 13.8954 14.1046 13 13 13C11.8954 13 11 13.8954 11 15C11 16.1046 11.8954 17 13 17Z" fill="#000000"/></svg>';
  var ICECREAM_SVG = '<svg width="800px" height="800px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M3.87447 8.48895C3.67833 4.10406 7.13384 0 12 0C16.8663 0 20.3218 4.10425 20.1255 8.48925C20.847 8.89205 21.3635 9.60473 21.4897 10.4841C21.641 11.5252 21.2508 12.4658 20.4345 13.0638C19.8243 13.5108 19.0428 13.7215 18.1956 13.7297L15.3522 18.9427L12.8779 23.4789C12.7027 23.8001 12.3659 24 12 24C11.6341 24 11.2973 23.8001 11.1221 23.4789L8.64794 18.9429L5.80374 13.7285C4.9581 13.719 4.17783 13.5085 3.56823 13.0624C2.75226 12.4654 2.36129 11.5264 2.51007 10.4855C2.63614 9.60351 3.15297 8.89129 3.87447 8.48895ZM5.86645 8.18707C6.25965 8.26168 6.60512 8.39708 6.8911 8.52005C7.04324 8.58547 7.17636 8.64529 7.29631 8.69919C7.65214 8.85909 7.89206 8.96691 8.16897 9.01438L8.1734 9.01515C8.64991 9.09904 8.93888 9.02985 9.47247 8.88068C9.48615 8.87685 9.49992 8.873 9.51379 8.86912C10.0875 8.70854 10.8325 8.5 12 8.5C13.1683 8.5 13.9143 8.70813 14.489 8.86849C14.5022 8.87217 14.5153 8.87583 14.5283 8.87945C15.0637 9.02865 15.353 9.09788 15.8279 9.01492C16.1044 8.96663 16.3436 8.85918 16.6966 8.70064C16.8184 8.64593 16.9538 8.58512 17.109 8.51857C17.3953 8.39573 17.7407 8.26089 18.1336 8.18665C18.1648 4.9573 15.5799 2 12 2C8.41992 2 5.83502 4.95756 5.86645 8.18707ZM8.22504 13.9909L9.6396 16.5843L10.8626 14.8721C10.1877 14.7286 9.55815 14.4886 9.01481 14.2814C8.94952 14.2565 8.88548 14.2321 8.82276 14.2084C8.6122 14.1288 8.41373 14.0557 8.22504 13.9909ZM13.1377 14.8721C13.8127 14.7285 14.4424 14.4885 14.9859 14.2813C15.0511 14.2565 15.1151 14.2321 15.1777 14.2084C15.388 14.1289 15.5863 14.0559 15.7748 13.9912L14.3605 16.5841L13.1377 14.8721ZM13.2963 18.5351L12.0001 16.7205L10.7038 18.5353L12 20.9117L13.2963 18.5351ZM17.6566 10.4643C17.2668 10.6415 16.7228 10.8889 16.1721 10.9851C15.2312 11.1494 14.5749 10.9687 13.9914 10.806C13.9799 10.8028 13.9685 10.7996 13.957 10.7964C13.4295 10.6493 12.8942 10.5 12 10.5C11.1075 10.5 10.5739 10.6493 10.0473 10.7967C10.0352 10.8 10.0231 10.8034 10.011 10.8068C9.42717 10.97 8.77106 11.1507 7.82868 10.9852C7.27424 10.8897 6.7288 10.6414 6.33868 10.4638C6.25109 10.4239 6.17133 10.3876 6.10105 10.3574C5.6422 10.1601 5.36987 10.0988 5.11393 10.1433C4.76351 10.2043 4.53647 10.443 4.48995 10.7685C4.44248 11.1006 4.54765 11.3008 4.74927 11.4484C4.99524 11.6283 5.48921 11.7911 6.2738 11.7059C7.49045 11.5737 8.62958 11.9971 9.53015 12.3376C9.56004 12.349 9.58971 12.3602 9.61916 12.3713C10.5605 12.7276 11.2805 13 12 13C12.7197 13 13.4402 12.7274 14.382 12.3711C14.4113 12.36 14.4407 12.3489 14.4704 12.3377C15.371 11.9972 16.5102 11.5737 17.7262 11.7059L17.7285 11.7061C18.5132 11.7932 19.007 11.6303 19.2526 11.4504C19.4539 11.3029 19.5587 11.1025 19.5105 10.7712L19.5101 10.7687C19.4637 10.4443 19.2356 10.2042 18.8861 10.1433C18.6293 10.0986 18.3558 10.1599 17.8975 10.3566C17.8264 10.3871 17.7455 10.4239 17.6566 10.4643Z" fill="#000000"/></svg>';
  var SODA_SVG = '<svg width="800px" height="800px" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M8.21922 0H12V2H9.78078L9.28078 4H14V6H2V4H7.21922L8.21922 0Z" fill="#000000"/><path d="M3.25 8L4 16H12L12.75 8H3.25Z" fill="#000000"/></svg>';
  var COFFEE_SVG = '<svg width="800px" height="800px" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4 0H2V3H4V0Z" fill="#000000"/><path fill-rule="evenodd" clip-rule="evenodd" d="M2 5H13C14.6569 5 16 6.34315 16 8V10C16 11.6569 14.6569 13 13 13H11.8293C11.4175 14.1652 10.3062 15 9 15H5C3.34315 15 2 13.6569 2 12V5ZM12 11V7H13C13.5523 7 14 7.44772 14 8V10C14 10.5523 13.5523 11 13 11H12Z" fill="#000000"/><path d="M10 0H12V3H10V0Z" fill="#000000"/><path d="M8 0H6V3H8V0Z" fill="#000000"/></svg>';
  var FRIES_SVG =
    '<svg width="800px" height="800px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">' +
    '<rect x="4.5" y="3" width="2" height="7" rx="1" fill="#000000"/>' +
    '<rect x="7" y="1.5" width="2" height="8.5" rx="1" fill="#000000"/>' +
    '<rect x="9.5" y="2.5" width="2" height="7.5" rx="1" fill="#000000"/>' +
    '<rect x="12" y="1.5" width="2" height="8.5" rx="1" fill="#000000"/>' +
    '<rect x="14.5" y="3" width="2" height="7" rx="1" fill="#000000"/>' +
    '<rect x="3.5" y="9.5" width="17" height="2" rx="0.75" fill="#000000"/>' +
    '<path fill-rule="evenodd" clip-rule="evenodd" d="M4.5 11L6 21.5C6.08 21.82 6.37 22 6.7 22H17.3C17.63 22 17.92 21.82 18 21.5L19.5 11H4.5ZM6.3 13L7.4 20.2H16.6L17.7 13H6.3Z" fill="#000000"/>' +
    '</svg>';
  var DONUT_SVG =
    '<svg width="800px" height="800px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">' +
    '<path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2ZM4 12C4 7.58172 7.58172 4 12 4C16.4183 4 20 7.58172 20 12C20 16.4183 16.4183 20 12 20C7.58172 20 4 16.4183 4 12ZM12 8.5C10.067 8.5 8.5 10.067 8.5 12C8.5 13.933 10.067 15.5 12 15.5C13.933 15.5 15.5 13.933 15.5 12C15.5 10.067 13.933 8.5 12 8.5ZM10.5 12C10.5 11.1716 11.1716 10.5 12 10.5C12.8284 10.5 13.5 11.1716 13.5 12C13.5 12.8284 12.8284 13.5 12 13.5C11.1716 13.5 10.5 12.8284 10.5 12Z" fill="#000000"/>' +
    '</svg>';

  var ITEM_IMAGES = {
    "Taco":      svgToDataUri(TACO_SVG),
    "Burger":    svgToDataUri(BURGER_SVG),
    "Hot Dog":   svgToDataUri(HOTDOG_SVG),
    "Pizza":     svgToDataUri(PIZZA_SVG),
    "Ice Cream": svgToDataUri(ICECREAM_SVG),
    "Soda":      svgToDataUri(SODA_SVG),
    "Coffee":    svgToDataUri(COFFEE_SVG),
    "Donut":     svgToDataUri(DONUT_SVG),
    "Fries":     svgToDataUri(FRIES_SVG)
  };

  // ─── MEMORY GAME ──────────────────────────────────────────────────────────
  function startMemoryGame(numOfPeople, numOfFoodTrucks, mapContainer, onSuccess, attempts, onAttempt, fixedSequence) {
  if (attempts === undefined) attempts = 0;
  var adjustedFoodTrucks = numOfFoodTrucks > 0 ? numOfFoodTrucks : 1;
  var customersPerTruck = Math.floor(numOfPeople / adjustedFoodTrucks);
  var sequenceLength = Math.min(3 + Math.floor(customersPerTruck / 10), 6);

    var possibleItems = [
      { name: "Taco",      image: ITEM_IMAGES["Taco"] },
      { name: "Burger",    image: ITEM_IMAGES["Burger"] },
      { name: "Hot Dog",   image: ITEM_IMAGES["Hot Dog"] },
      { name: "Pizza",     image: ITEM_IMAGES["Pizza"] },
      { name: "Ice Cream", image: ITEM_IMAGES["Ice Cream"] },
      { name: "Soda",      image: ITEM_IMAGES["Soda"] },
      { name: "Coffee",    image: ITEM_IMAGES["Coffee"] },
      { name: "Donut",     image: ITEM_IMAGES["Donut"] },
      { name: "Fries",     image: ITEM_IMAGES["Fries"] }
    ];

    function toCode(seq) {
      return seq.map(function(x) { return x.name.charAt(0).toUpperCase(); }).join("");
    }

   var sequence = fixedSequence || (function() {
  var maxLen = Math.min(sequenceLength, possibleItems.length);
  var shuffled = possibleItems.slice().sort(function() { return 0.5 - Math.random(); });
  return shuffled.slice(0, maxLen);
})();
var correctCode = toCode(sequence);

    var sequenceDisplay = document.createElement("div");
    sequenceDisplay.id = "sequence-display";
    var inputContainer = document.createElement("div");
    inputContainer.id = "input-container";

    mapContainer.appendChild(sequenceDisplay);
    mapContainer.appendChild(inputContainer);

    var displayIndex = 0;
    function displayNextItem() {
      if (displayIndex < sequence.length) {
        sequenceDisplay.innerHTML = "";
        var img = document.createElement("img");
        img.src = sequence[displayIndex].image;
        img.alt = sequence[displayIndex].name;
        img.classList.add("sequence-item");
        sequenceDisplay.appendChild(img);
        displayIndex++;
        setTimeout(displayNextItem, 2000);
      } else {
        sequenceDisplay.innerHTML = "";
        showInputButtons();
      }
    }
    displayNextItem();

    function showInputButtons() {
      inputContainer.innerHTML = "";
      var playerSequence = [];
      var shuffledPossible = possibleItems.slice().sort(function() { return 0.5 - Math.random(); });

      shuffledPossible.forEach(function(item) {
        var btn = document.createElement("button");
        btn.classList.add("input-button");
        var img = document.createElement("img");
        img.src = item.image;
        img.alt = item.name;
        img.classList.add("input-item");
        btn.appendChild(img);

        btn.addEventListener("click", function() {
          playerSequence.push(item);
          btn.classList.add("selected");

          if (playerSequence.length === sequence.length) {
            var playerCode = toCode(playerSequence);
            var isCorrect = sequencesMatch(playerSequence, sequence);
            var nextAttemptNumber = attempts + 1;

            if (typeof onAttempt === "function") {
              try {
                onAttempt({ attemptNumber: nextAttemptNumber, playerCode: playerCode, correctCode: correctCode, isCorrect: isCorrect });
              } catch(e) {}
            }

            if (isCorrect) {
              sequenceDisplay.remove();
              inputContainer.remove();
              onSuccess(attempts, correctCode);
            } else {
              sequenceDisplay.remove();
              inputContainer.remove();
              attempts++;
              if (attempts >= 4) {
                onSuccess(attempts, correctCode);
                return;
              }
              alert("Incorrect sequence. Please try again.");
              startMemoryGame(numOfPeople, numOfFoodTrucks, mapContainer, onSuccess, attempts, onAttempt, sequence);
            }
          }
        });
        inputContainer.appendChild(btn);
      });
    }

    function sequencesMatch(s1, s2) {
      if (s1.length !== s2.length) return false;
      for (var i = 0; i < s1.length; i++) { if (s1[i].name !== s2[i].name) return false; }
      return true;
    }
  }

  // ─── PARK ─────────────────────────────────────────────────────────────────
  function Park(randomize, numOfDays, numOfHours, numOfPeople, numOfFoodTrucks) {
    if (numOfPeople === undefined) numOfPeople = [];
    if (numOfFoodTrucks === undefined) numOfFoodTrucks = [];
    Park.numOfParks = (Park.numOfParks || 0) + 1;
    this.name = "Park " + Park.numOfParks;
    this.numOfPeople = numOfPeople;
    this.numOfFoodTrucks = numOfFoodTrucks;

    if (randomize) {
      this.numOfPeople = [];
      this.numOfFoodTrucks = [];
      var pArr = [], tArr = [];
      for (var i = 0; i < numOfHours * numOfDays; i++) {
        pArr.push(randomInteger(1, 100));
        tArr.push(randomInteger(1, 10));
        if ((i + 1) % numOfHours === 0) {
          this.numOfPeople.push(pArr);
          this.numOfFoodTrucks.push(tArr);
          pArr = []; tArr = [];
        }
      }
    }
  }
  Park.prototype.getNumOfPeople     = function(d, h) { return this.numOfPeople[d][h]; };
  Park.prototype.getNumOfFoodTrucks = function(d, h) { return this.numOfFoodTrucks[d][h]; };

  // ─── GAME STATE ───────────────────────────────────────────────────────────
  function GameState(randomize, hints, numOfParks, numOfDays, numOfHours, numOfPeople, numOfFoodTrucks, hooks, historyDepthArg, socialInfoArg, adviceScheduleArg) {
    if (!hints) hints = [];
    if (numOfParks === undefined)  numOfParks  = 4;
    if (numOfDays === undefined)   numOfDays   = 5;
    if (numOfHours === undefined)  numOfHours  = 8;
    if (!numOfPeople)     numOfPeople = [];
    if (!numOfFoodTrucks) numOfFoodTrucks = [];

    this.numOfParks   = numOfParks;
    this.numOfDays    = numOfDays;
    this.numOfHours   = numOfHours;
    this.currentPark  = null;
    this.profits      = 0;
    this.parks        = [];
    this.currentDay   = 0;
    this.currentHour  = 0;
    this.hints        = hints;
    this.dayListItems = {};
    this.eventLists   = {};
    this.hooks        = hooks || {};
    this.events       = [];
	  
    this.historyDepth = (typeof historyDepthArg === 'string' && historyDepthArg !== '') ? historyDepthArg : 'none';
	this.socialInfo = (typeof socialInfoArg === 'string' && socialInfoArg !== '') ? socialInfoArg : 'on';
	this.adviceSchedule = adviceScheduleArg || null;
	  
    Park.numOfParks   = 0;

    for (var i = 0; i < numOfParks; i++) {
      this.parks.push(
        randomize
          ? new Park(true, numOfDays, numOfHours)
          : new Park(false, numOfDays, numOfHours, numOfPeople[i], numOfFoodTrucks[i])
      );
    }
    this.currentPark = this.parks[0];
    this.createMenu();
  }

  GameState.prototype.log = function(evt) {
    this.events.push(evt);
    if (typeof this.hooks.onEvent === "function") {
      try { this.hooks.onEvent(evt); } catch(e) {}
    }
  };

  // ── Observation panel ─────────────────────────────────────────────────────
  GameState.prototype.displayNumberOfMovingTrucks = function(isArriving) {
    var obs   = document.getElementById("observation-text-container");
    var desc  = document.getElementById("observation-description-text");
    var arrTx = document.getElementById("arrival-text");
    var depTx = document.getElementById("departure-text");

    if (!this.currentPark || this.currentDay < 0 || this.currentHour < 0) { hide(obs); return; }
    if (isArriving  && this.currentHour === 0)                             { hide(obs); return; }
    if (!isArriving && this.currentHour >= this.numOfHours - 1)            { hide(obs); return; }


    var curr  = this.currentPark.getNumOfFoodTrucks(this.currentDay, this.currentHour);
    var compH = isArriving ? (this.currentHour - 1) : (this.currentHour + 1);
    var comp  = this.currentPark.getNumOfFoodTrucks(this.currentDay, compH);
    if (curr === undefined || comp === undefined) { hide(obs); return; }

    var diff = comp - curr;
    if (isArriving) diff *= -1;

    arrTx.textContent = "Trucks Arriving at Park: " + (diff > 0 ? diff : 0);
    depTx.textContent = "Trucks Leaving Park: "     + (diff < 0 ? -diff : 0);
    desc.textContent  = isArriving
      ? "As you arrive at the park you notice the following:"
      : "As you decide where to go next you notice the following:";
	if (this.socialInfo === 'off') { hide(obs); } else { show(obs); }  };

  // ── Tip rating widget ─────────────────────────────────────────────────────
  GameState.prototype.showTipWithRating = function(hintIndex, hintText, onRated) {
    var self = this;
    var tipContainer = document.getElementById("tip-rating-container");
    var tipTextEl    = document.getElementById("tip-text-display");
    var ratedLabel   = document.getElementById("tip-rated-label");
    var thumbsUp     = document.getElementById("tip-thumbs-up");
    var thumbsDown   = document.getElementById("tip-thumbs-down");

    tipTextEl.textContent  = hintText;
    ratedLabel.textContent = "Rate this tip to continue ↑↓";
    ratedLabel.style.color = "#9333ea";
    thumbsUp.classList.remove("rated", "chosen");
    thumbsDown.classList.remove("rated", "chosen");

    function rateHandler(rating) {
      thumbsUp.classList.add("rated");
      thumbsDown.classList.add("rated");
      if (rating === "up")   thumbsUp.classList.add("chosen");
      if (rating === "down") thumbsDown.classList.add("chosen");
      ratedLabel.textContent = "Thanks for your feedback!";
      ratedLabel.style.color = "#6366f1";
      self.log({ type: "tip_rating", day: self.currentDay + 1, hour: self.currentHour + 1, hintIndex: hintIndex, rating: rating });
      if (typeof onRated === "function") onRated();
    }

    thumbsUp.onclick   = function() { rateHandler("up"); };
    thumbsDown.onclick = function() { rateHandler("down"); };
    show(tipContainer);
  };

  // ── Expected profit display ───────────────────────────────────────────────
  GameState.prototype.updateExpectedProfit = function(attempts) {
    var el = document.getElementById("expected-profit-display");
    if (!el || !this.currentPark) return;
    var numPeople = this.currentPark.getNumOfPeople(this.currentDay, this.currentHour);
    var numTrucks = this.currentPark.getNumOfFoodTrucks(this.currentDay, this.currentHour);
    var base = Math.ceil(numPeople / (numTrucks + 1));
    var minC = Math.max(1, base - 2);
    var maxC = Math.max(1, base + 4);
    var penalty = 1 - 0.25 * attempts;
    var minP = Math.round(minC * 8  * penalty);
    var maxP = Math.round(maxC * 25 * penalty);
    el.textContent = "💰 Est. profit: $" + minP + " – $" + maxP +
      (attempts > 0 ? " (–" + (attempts * 25) + "% penalty)" : "");
    show(el);
  };

  // ── Main menu / UI wiring ─────────────────────────────────────────────────
  GameState.prototype.createMenu = function() {
    var self = this;
    var mapContainer     = document.getElementById("map");
    var profitGainsText  = document.getElementById("profit-gains");
    var historyContainer = document.getElementById("history-container");

    // History panel
    var histHeader = document.createElement("h2");
    histHeader.textContent = "History:";
    historyContainer.appendChild(histHeader);
    var histList = document.createElement("ul");
    histList.id = "history-list";
    historyContainer.appendChild(histList);

    // Map panel header
    var mapHeader = document.createElement("h2");
    mapHeader.textContent = "Choose which park to travel to...";
    mapContainer.appendChild(mapHeader);

    // Observation panel
    var obs  = document.createElement("div"); obs.id = "observation-text-container";
    var desc = document.createElement("p");   desc.id = "observation-description-text";
    var arrT = document.createElement("p");   arrT.id = "arrival-text";
    var depT = document.createElement("p");   depT.id = "departure-text";
    obs.appendChild(desc); obs.appendChild(arrT); obs.appendChild(depT);
    mapContainer.appendChild(obs);
    hide(obs);

    // Tip rating panel
    var tipContainer = document.createElement("div");
    tipContainer.id = "tip-rating-container";
    tipContainer.innerHTML = `
      <p>💡 Tip for this hour:</p>
      <p id="tip-text-display" class="tip-text"></p>
      <div id="tip-rating-buttons">
        <button id="tip-thumbs-up"   class="tip-rate-btn" title="Helpful">👍</button>
        <button id="tip-thumbs-down" class="tip-rate-btn" title="Not helpful">👎</button>
        <span id="tip-rated-label"></span>
      </div>
    `;
    mapContainer.appendChild(tipContainer);
    hide(tipContainer);

    // Button container
    var buttonContainer = document.createElement("div");
    buttonContainer.id = "button-container";
    mapContainer.appendChild(buttonContainer);

    // "Begin serving" button
    var startBtn = document.createElement("button");
    startBtn.id = "minigame-start-button";
    startBtn.textContent = "Begin serving food!";
    buttonContainer.appendChild(startBtn);
    hide(startBtn);

    // "New day" button
    var continueBtn = document.createElement("button");
    continueBtn.id = "continue-button";
    continueBtn.textContent = "Start a new day!";
    mapContainer.appendChild(continueBtn);
    hide(continueBtn);

    // Park buttons
    for (var i = 0; i < this.numOfParks; i++) {
      (function(idx) {
        var btn = document.createElement("button");
        btn.classList.add("park-button");
        btn.classList.add("park-color-" + (idx % 6));
        var parkEmojis = ["🌳", "🏞️", "⛲", "🌺", "🏕️", "🎡"];
        btn.textContent = parkEmojis[idx % parkEmojis.length] + " " + self.parks[idx].name;
        buttonContainer.appendChild(btn);

        btn.addEventListener("click", function() {
          self.currentPark = self.parks[idx];
		  updateText("current-park", self.currentPark.name);
          self.log({ type: "choose_park", day: self.currentDay + 1, hour: self.currentHour + 1, park: self.currentPark.name });

          document.querySelectorAll(".park-button").forEach(function(b) { hide(b); });
          hide(document.getElementById("tip-rating-container"));
          hide(document.getElementById("profit-preview-container"));

          if (self.currentHour === 0) {
            var ppl = self.currentPark.getNumOfPeople(self.currentDay, 0);
            var trk = self.currentPark.getNumOfFoodTrucks(self.currentDay, 0);
            document.getElementById("observation-description-text").textContent = "As you arrive at " + self.currentPark.name + " you see:";
            document.getElementById("arrival-text").textContent = "👤 People at park: " + ppl;
            document.getElementById("departure-text").textContent = "🚚 Food trucks present: " + trk;
            if (self.socialInfo === 'off') { hide(obs); } else { show(obs); }
          } else {
            self.displayNumberOfMovingTrucks(true);
          }
          mapHeader.textContent = "Arriving at " + self.currentPark.name;

          var ppl = self.currentPark.getNumOfPeople(self.currentDay, self.currentHour);
          var trk = self.currentPark.getNumOfFoodTrucks(self.currentDay, self.currentHour);
          var minCustomers = Math.max(1, -2 + Math.ceil(ppl / (trk + 1)));
          var maxCustomers = Math.max(1,  4 + Math.ceil(ppl / (trk + 1)));
          updateText("preview-people",       "👤 People: " + ppl);
          updateText("preview-trucks",       "🚚 Trucks: " + trk);
          updateText("preview-profit-range", "💰 Est. profit: $" + (minCustomers * 8) + " – $" + (maxCustomers * 25));
          self.updateExpectedProfit(0);
          show(startBtn);
        });
      })(i);
    }

    // "Begin serving" click
    startBtn.addEventListener("click", function() {
      hide(startBtn);
      hide(obs);
      hide(document.getElementById("tip-rating-container"));
      mapHeader.textContent = "Memorize the customer's orders...";

      var numPeople = self.currentPark.getNumOfPeople(self.currentDay, self.currentHour);
      var numTrucks = self.currentPark.getNumOfFoodTrucks(self.currentDay, self.currentHour);

      self.log({ type: "start_minigame", day: self.currentDay + 1, hour: self.currentHour + 1, park: self.currentPark.name, people: numPeople, trucks: numTrucks });

      startMemoryGame(
        numPeople, numTrucks, mapContainer,
        function(attempts, correctCode) {
          self.generateProfit(self.currentDay, self.currentHour, attempts, correctCode);
          show(profitGainsText);

          var isLastHour = (self.currentHour >= self.numOfHours - 1);

          if (isLastHour) {
            mapHeader.textContent = "Day complete!";
            hide(obs);
            hide(document.getElementById("tip-rating-container"));
            hide(document.getElementById("expected-profit-display"));
            show(continueBtn);
          } else {
            self.displayNumberOfMovingTrucks(false);
            mapHeader.textContent = "Decision for the next hour:";
            hide(document.getElementById("expected-profit-display"));

            var showAdvice = true;
if (self.adviceSchedule) {
  var schedDay  = self.adviceSchedule[self.currentDay];
  showAdvice = schedDay ? (schedDay[self.currentHour] === 1) : false;
}

if (showAdvice) {
  var nextHour = self.currentHour + 1;
  var bestPark = self.parks[0], worstPark = self.parks[0];
  var minTrucks = Infinity, maxTrucks = -Infinity;
  self.parks.forEach(function(park) {
    var t = park.getNumOfFoodTrucks(self.currentDay, nextHour);
    if (t < minTrucks) { minTrucks = t; bestPark = park; }
    if (t > maxTrucks) { maxTrucks = t; worstPark = park; }
  });

  var targetPark = (self.congruence === 'incongruent') ? worstPark : bestPark;
  var tipText = "💡 Tip: We recommend heading to " + targetPark.name + " next hour!";

  self.log({ type: "hint", day: self.currentDay + 1, hour: self.currentHour + 1, park: targetPark.name, congruence: self.congruence });
  self.showTipWithRating(0, tipText, function() {
    document.querySelectorAll(".park-button").forEach(function(b) { show(b); });
  });
} else {
  document.querySelectorAll(".park-button").forEach(function(b) { show(b); });
}
          }

          self.currentHour++;
          updateText("current-day",          self.currentDay + 1);
          updateText("current-hour-display", Math.min(self.currentHour + 1, self.numOfHours));
        },
        0,
        function(info) {
          self.log({ type: "memory_attempt", day: self.currentDay + 1, hour: self.currentHour + 1, park: self.currentPark.name, people: numPeople, trucks: numTrucks, attemptNumber: info.attemptNumber, playerCode: info.playerCode, correctCode: info.correctCode, isCorrect: info.isCorrect });
          if (!info.isCorrect) { self.updateExpectedProfit(info.attemptNumber); }
        }
      );
    });

    // "New day" click
    continueBtn.addEventListener("click", function() {
      hide(profitGainsText);
      hide(continueBtn);
      if (self.nextDay()) {
        show(mapHeader);
        show(buttonContainer);
        document.querySelectorAll(".park-button").forEach(function(b) { show(b); });
      }
    });
  };

  // ── nextDay ───────────────────────────────────────────────────────────────
  GameState.prototype.nextDay = function() {
    this.currentHour = 0;
    this.currentDay++;

    if (this.currentDay >= this.numOfDays) {
      this.currentDay = this.numOfDays - 1;
      this.endGame();
      return false;
    }

    updateText("current-park",          "Home");
    updateText("number-of-people",      "");
    updateText("number-of-food-trucks", "");
    updateText("current-day",           this.currentDay + 1);
    updateText("final-hour",            this.numOfHours);
    updateText("current-hour-display",  this.currentHour + 1);

    var mapHeader = document.querySelector("#map h2");
    if (mapHeader) mapHeader.textContent = "Choose which park to travel to...";
    return true;
  };

  // ── generateProfit ────────────────────────────────────────────────────────
  GameState.prototype.generateProfit = function(day, hour, attempts, correctCode) {
    var histList     = document.getElementById("history-list");
    var numPeople    = this.currentPark.getNumOfPeople(day, hour);
    var numTrucks    = this.currentPark.getNumOfFoodTrucks(day, hour);
    var numCustomers = Math.max(1, randomInteger(-2, 4) + Math.ceil(numPeople / (numTrucks + 1)));

    var profit = numCustomers * randomInteger(8, 25);
    profit -= profit * 0.25 * attempts;
    this.profits += profit;

    var dayNum  = this.currentDay + 1;
    var dayItem = this.dayListItems[dayNum];
    if (!dayItem) {
      dayItem = document.createElement("li");
      dayItem.textContent = "Day " + dayNum;
      var evList = document.createElement("ul");
      dayItem.appendChild(evList);
      histList.insertBefore(dayItem, histList.firstChild);
      this.dayListItems[dayNum] = dayItem;
      this.eventLists[dayNum]   = evList;
    }

    var evItem = document.createElement("li");
    evItem.textContent = "H" + (this.currentHour + 1) + ": Profited $" + profit + " at " + this.currentPark.name + ". " + numPeople + " people, " + numTrucks + " trucks.";
    this.eventLists[dayNum].insertBefore(evItem, this.eventLists[dayNum].firstChild);

    document.getElementById("history-container").scrollTop = 0;

    updateText("current-park",          this.currentPark.name);
    updateText("profit-gains",          "You gained $" + profit);
    updateText("current-profit",        this.profits);
    updateText("number-of-people",      "👤👤👤: " + numPeople);
    updateText("number-of-food-trucks", "🚚🥡: " + numTrucks);

    this.pruneHistory();

    this.log({ type: "profit", day: this.currentDay + 1, hour: this.currentHour + 1, park: this.currentPark.name, profitsFromHour: profit, totalProfits: this.profits, people: numPeople, trucks: numTrucks, attempts: attempts, correctCode: correctCode || "" });
  };

  // ── pruneHistory ──────────────────────────────────────────────────────────
  GameState.prototype.pruneHistory = function() {
    var limit = this.historyDepth === 'short' ? 1
              : this.historyDepth === 'long'  ? 5
              : null;
    if (limit === null) return;

    var self     = this;
    var histList = document.getElementById("history-list");
    if (!histList) return;

    // Collect all hour-level <li> items, newest first
    var allHourItems = [];
    var dayItems = histList.querySelectorAll(":scope > li");
    dayItems.forEach(function(dayLi) {
      dayLi.querySelectorAll(":scope > ul > li").forEach(function(li) {
        allHourItems.push(li);
      });
    });

    // Remove any entries beyond the limit
    for (var i = limit; i < allHourItems.length; i++) {
      allHourItems[i].parentNode.removeChild(allHourItems[i]);
    }

    // Remove day headers that are now empty, and clear bookkeeping so they regenerate
    dayItems.forEach(function(dayLi) {
      var subUl = dayLi.querySelector("ul");
      if (subUl && subUl.children.length === 0) {
        var match = dayLi.textContent.match(/^Day (\d+)/);
        if (match) {
          var dayNum = parseInt(match[1], 10);
          delete self.dayListItems[dayNum];
          delete self.eventLists[dayNum];
        }
        dayLi.parentNode.removeChild(dayLi);
      }
    });
  };

  // ── endGame ───────────────────────────────────────────────────────────────
  GameState.prototype.endGame = function() {
    updateText("current-park",          "GAME OVER");
    updateText("number-of-people",      "Thanks for playing!");
    updateText("number-of-food-trucks", "");
    updateText("profit-gains",          "");

    this.log({ type: "end", totalProfits: this.profits });

    if (typeof this.hooks.onFinish === "function") {
      try { this.hooks.onFinish({ totalProfit: this.profits, events: this.events }); } catch(e) {}
    }
  };

  // ─── BOOT ─────────────────────────────────────────────────────────────────
  var hints = [
    "The early bird catches the... burrito? Try Park 2 this hour.",
    "A yoga class just ended at Park 4. Expect a crowd hungry for green smoothies.",
    "Beware! Park 2 is attracting a swarm of toddlers. Deploy the mac and cheese truck!",
    "Park 2: Where fries are eaten faster than they can be made. Join the fry frenzy!",
    "A band just started playing at Park 4. Brace for a mosh pit at the taco truck!",
    "They say Park 3's ice cream truck just ran out of cones. Time to bring some backup!",
    "Park 1 has a dog parade. Bring extra hot dogs – for the humans!",
    "Rumor has it Park 4 just ran out of napkins – prepare for sticky fingers!",
    "Park 1: The only place where people still believe fries count as a vegetable.",
    "Park 3: Where the line is always longer than the food supply.",
    "Reminder: Ice cream melts in Park 4 faster than decisions are made here.",
    "Park 2: Now with 20% more 'Oh, I thought this was the taco truck.'",
    "Park 3: Where every decision is just a very long wait in disguise.",
    "Park 4 is currently experiencing a 'We don't have that' shortage.",
    "Rumor has it that Park 1 has WiFi. Also, people there occasionally buy food.",
    "Park 2: Serving the existentially hungry since... well, this hour.",
    "Park 4: Free napkins are limited, use sparingly or not at all.",
    "If lost, head to Park 3. You won't find directions, but you will find people asking for them.",
    "Park 1: Now with 10% more food trucks and 90% more people wondering why.",
    "Someone at Park 2 asked for a salad. This was not well received.",
    "Park 4: Come for the food, stay because you're still waiting for it.",
    "Park 3: Where every hot dog has a 50/50 chance of being the last one.",
    "Please note: The fries in Park 1 are now considered a limited edition.",
    "Park 4: Less a food experience, more an exercise in patience.",
    "Park 1 just got a new truck! No one knows what it serves yet.",
    "In Park 3, they say if you stare long enough, a truck might appear."
  ];

  var exportObj = { startedAt: Date.now(), events: [] };

  function onEvent(evt) {
    exportObj.events.push(Object.assign({ t: Date.now() }, evt));
  }

  function onFinish(summary) {
    exportObj.finishedAt = Date.now();
    exportObj.summary    = summary || {};
    var tp = (summary && summary.totalProfit != null) ? summary.totalProfit : "";
    Qualtrics.SurveyEngine.setEmbeddedData("bobalab_total_profit", String(tp));
    Qualtrics.SurveyEngine.setEmbeddedData("bobalab_json", JSON.stringify(exportObj));
    q.clickNextButton();
  }

  try {
    var experiment      = 0;
	  
    var adviceFreqIdx   = 0;
    var historyDepthIdx = 0;
    var advice_freq     = '';
    var history_depth   = '';
	  
	var sparse = [
		[0,0],
		[0,0],
	]
	var frequent = [
		[1,0],
		[1,1],
	]
	
    var advice_freqs    = [null, sparse, frequent];
    var history_depths  = ['none', 'short', 'long'];
	  
	var socialInfoIdx = 0;
	var congruenceIdx = 0;
	var social_info = '';
	var congruence = '';
	var social_infos = ['none', 'on', 'off'];
	var congruences = ['none', 'congruent', 'incongruent'];

    // experiment = parseInt(getED("experiment", 0), 10) || 0;
	experiment = 2;
    if (experiment === 1) {
      adviceFreqIdx   = parseInt(getED("advice_freq",   0), 10) || 0;
	  adviceFreqIdx = 2;
      historyDepthIdx = parseInt(getED("history_depth", 0), 10) || 0;
	  historyDepthIdx = 1;
	
      advice_freq     = advice_freqs[adviceFreqIdx];
      history_depth   = history_depths[historyDepthIdx];
		
    } else if (experiment === 2) {
		//socialInfoIdx = parseInt(getED("social_info",   0), 10) || 0;
		socialInfoIdx = 2;
		congruenceIdx = parseInt(getED("congruence",   0), 10) || 0;
		social_info = social_infos[socialInfoIdx];
		congruence = congruences[congruenceIdx];
	}
	 

    var gameState = new GameState(true, hints, 2, 2, 2, [], [], { onEvent: onEvent, onFinish: onFinish }, history_depth, social_info, advice_freq);
    updateText("final-day",            gameState.numOfDays);
    updateText("final-hour",           gameState.numOfHours);
    updateText("current-day",          gameState.currentDay  + 1);
    updateText("current-hour-display", gameState.currentHour + 1);
  } catch(e) {
    root.innerHTML = "<p><b>BobaLab failed to start:</b> " + (e && e.message ? e.message : String(e)) + "</p>";
    q.showNextButton();
  }
});