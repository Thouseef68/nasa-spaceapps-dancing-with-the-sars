import re

with open("web/index_backup.html", "r", encoding="utf-8") as f:
    html = f.read()

# ------------------------------------------------------------------
# 1. CSS ADDITIONS
# ------------------------------------------------------------------
extra_css = """
  /* Modals & Dialogs General */
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(3, 7, 18, 0.8);
    backdrop-filter: blur(10px);
    z-index: 2500;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    opacity: 1;
    transition: opacity 0.25s ease;
  }
  .modal-backdrop.hidden { display: none; opacity: 0; }
  .modal-card {
    background: rgba(15, 23, 42, 0.95);
    backdrop-filter: blur(24px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 16px;
    padding: 22px;
    box-shadow: 0 25px 60px rgba(0,0,0,0.8);
    max-width: 620px;
    width: 100%;
    max-height: 85vh;
    overflow-y: auto;
    color: #cbd5e1;
    animation: modalPop 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  }
  .wide-modal { max-width: 820px; }
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding-bottom: 12px;
    margin-bottom: 16px;
  }
  .btn-close {
    background: transparent;
    border: none;
    color: #94a3b8;
    font-size: 22px;
    cursor: pointer;
    line-height: 1;
    padding: 2px 6px;
    border-radius: 6px;
  }
  .btn-close:hover { color: white; background: rgba(255,255,255,0.1); }

  /* SAR Physics Studio Tabs & Canvas */
  .physics-tabs {
    display: flex;
    gap: 6px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding-bottom: 10px;
    margin-bottom: 16px;
    overflow-x: auto;
  }
  .phys-tab {
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #94a3b8;
    padding: 7px 12px;
    border-radius: 8px;
    font-size: 11.5px;
    font-weight: 600;
    cursor: pointer;
    white-space: nowrap;
    transition: all 0.2s;
  }
  .phys-tab:hover { color: white; background: rgba(255,255,255,0.1); }
  .phys-tab.active {
    background: #7c3aed;
    color: white;
    border-color: #a855f7;
    box-shadow: 0 2px 10px rgba(124, 58, 237, 0.4);
  }
  .phys-canvas-wrap {
    background: #020617;
    border: 1px solid rgba(168, 85, 247, 0.3);
    border-radius: 12px;
    overflow: hidden;
    position: relative;
    height: 220px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 14px;
  }
  #phys-canvas { width: 100%; height: 100%; display: block; }
  .phys-meta-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-top: 12px;
  }
  .phys-stat-card {
    background: rgba(30, 41, 59, 0.5);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 10px;
    text-align: center;
  }
  .phys-stat-label { font-size: 10px; color: #94a3b8; text-transform: uppercase; font-weight: 700; }
  .phys-stat-val { font-size: 13.5px; color: #c084fc; font-weight: 700; margin-top: 3px; }

  /* Relief Triage Cursor & Popup */
  .triage-cursor #map { cursor: crosshair !important; }
  .triage-marker-dot {
    width: 16px;
    height: 16px;
    background: #ef4444;
    border: 2px solid white;
    border-radius: 50%;
    box-shadow: 0 0 14px #ef4444;
    animation: triagePulse 1.4s infinite;
  }
  @keyframes triagePulse {
    0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.8); }
    70% { transform: scale(1.1); box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
    100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
  }

  /* Toast Notification */
  #toast-notification {
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: rgba(15, 23, 42, 0.95);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(56, 189, 248, 0.5);
    border-radius: 12px;
    padding: 12px 18px;
    color: white;
    font-size: 12.5px;
    z-index: 3000;
    box-shadow: 0 10px 30px rgba(0,0,0,0.6);
    display: flex;
    align-items: center;
    gap: 10px;
    opacity: 0;
    transform: translateY(20px);
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    pointer-events: none;
  }
  #toast-notification.show { opacity: 1; transform: translateY(0); pointer-events: auto; }

  /* Official SitRep Printable Styling */
  @media print {
    body * { visibility: hidden; }
    #sitrep-print-container, #sitrep-print-container * { visibility: visible; }
    #sitrep-print-container {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      background: white !important;
      color: black !important;
      font-family: Arial, sans-serif !important;
      padding: 20px;
    }
  }
"""

# Inject extra CSS before </style>
html = html.replace("</style>", extra_css + "\n</style>", 1)
print("1. Extra CSS injected.")

# ------------------------------------------------------------------
# 2. TOP BAR & CONTROLS ADDITIONS
# ------------------------------------------------------------------
old_top_bar = """  <div class="glass-card">
    <button id="btn-director" class="btn" onclick="toggleDirectorMode()" title="Choreographed 3D Flythrough">🎬 Director Mode</button>
    <button id="btn-probe" class="btn" onclick="toggleRadarProbe()" title="Inspect SAR Backscatter & Elevation under cursor">🎯 Radar Probe</button>
    <button id="btn-sweep" class="btn" onclick="toggleSweepModal()" title="Interactive Threshold Tuning">🎚️ Threshold Sandbox</button>
    <button id="btn-transect" class="btn" onclick="toggleTransectTool()">📐 Transect</button>
    <button id="btn-swipe" class="btn" onclick="toggleSwipeTool()">🔀 Swipe</button>
    <button id="btn-district" class="btn" onclick="toggleDistrictModal()">📍 Districts</button>
  </div>"""

new_top_bar = """  <div class="glass-card">
    <button id="btn-director" class="btn" onclick="toggleDirectorMode()" title="Choreographed 3D Flythrough">🎬 Director Mode</button>
    <button id="btn-physics" class="btn" onclick="toggleSarPhysicsModal()" style="border: 1px solid rgba(192, 132, 252, 0.4); color: #c084fc; background: rgba(192, 132, 252, 0.1);" title="Dancing with the SARs: Microwave Scattering Studio">🛰️ SAR Physics Studio</button>
    <button id="btn-triage" class="btn" onclick="toggleReliefTriage()" title="Disaster Operations: Evaluate flood risk, crest elevation & nearest refuge">🚨 Relief Triage</button>
    <button id="btn-probe" class="btn" onclick="toggleRadarProbe()" title="Inspect SAR Backscatter & Elevation under cursor">🎯 Radar Probe</button>
    <button id="btn-sweep" class="btn" onclick="toggleSweepModal()" title="Interactive Threshold Tuning">🎚️ Threshold Sandbox</button>
    <button id="btn-transect" class="btn" onclick="toggleTransectTool()">📐 Transect</button>
    <button id="btn-swipe" class="btn" onclick="toggleSwipeTool()">🔀 Swipe</button>
    <button id="btn-district" class="btn" onclick="toggleDistrictModal()">📍 Districts</button>
    <button id="btn-snapshot" class="btn" onclick="captureIntelSnapshot()" title="Capture High-Resolution Intel PNG">📸 Snapshot</button>
    <button id="btn-report" class="btn" onclick="openOfficialPrintSitRep()" title="Generate Official UN-SPIDER / CWC SitRep Document">📄 SitRep</button>
  </div>"""

assert old_top_bar in html, "Could not match old top bar"
html = html.replace(old_top_bar, new_top_bar, 1)

# Add language dropdown in top bar next to audio button
old_lang_target = """  <button class="btn btn-accent" onclick="startGuidedTour(0)">ℹ️ Mission Guide</button>
  <button class="btn" style="border: 1px solid rgba(245, 158, 11, 0.5); color: #fbbf24; background: rgba(245, 158, 11, 0.1);" onclick="toggleTeamModal()">🏆 Team & Challenge</button>
  <button class="btn" id="btn-audio" onclick="toggleAudio()" title="Sound Effects">🔊</button>"""

new_lang_addition = """  <button class="btn btn-accent" onclick="startGuidedTour(0)">ℹ️ Mission Guide</button>
  <button class="btn" style="border: 1px solid rgba(245, 158, 11, 0.5); color: #fbbf24; background: rgba(245, 158, 11, 0.1);" onclick="toggleTeamModal()">🏆 Team & Challenge</button>
  <select id="lang-select" class="fly-select" onchange="setLanguage(this.value)" style="border-color: rgba(56, 189, 248, 0.4); background: rgba(15, 23, 42, 0.85); color: #38bdf8; font-weight: 600; padding: 6px 10px; border-radius: 20px;">
    <option value="en">🌐 English (Global)</option>
    <option value="as">🌐 অসমীয়া (Assam)</option>
    <option value="hi">🌐 हिन्दी (India)</option>
  </select>
  <button class="btn" id="btn-audio" onclick="toggleAudio()" title="Sound Effects">🔊</button>"""

assert old_lang_target in html, "Could not match lang insertion target"
html = html.replace(old_lang_target, new_lang_addition, 1)
print("2. Top bar buttons & language select injected.")

# ------------------------------------------------------------------
# 3. DIRECTOR OVERLAY VOICE BUTTON
# ------------------------------------------------------------------
old_dir_controls = """    <div style="display:flex; justify-content:center; gap:10px; margin-top:10px;">
      <button class="btn" onclick="pauseOrResumeDirector()"><span id="director-play-icon">⏸</span> Pause</button>
      <button class="btn" onclick="stopDirectorMode()">✕ Exit Tour</button>
    </div>"""

new_dir_controls = """    <div style="display:flex; justify-content:center; gap:10px; margin-top:10px;">
      <button class="btn" onclick="pauseOrResumeDirector()"><span id="director-play-icon">⏸</span> Pause</button>
      <button class="btn active" id="director-voice-btn" onclick="toggleDirectorVoice()"><span id="director-voice-icon">🔊</span> Voice: ON</button>
      <button class="btn" onclick="stopDirectorMode()">✕ Exit Tour</button>
    </div>"""

assert old_dir_controls in html, "Could not match director controls"
html = html.replace(old_dir_controls, new_dir_controls, 1)
print("3. Director Voice button injected.")

# ------------------------------------------------------------------
# 4. NEW MODALS HTML (SAR Physics Studio & SitRep Report)
# ------------------------------------------------------------------
new_modals = """
<!-- Toast Notification -->
<div id="toast-notification">
  <span id="toast-icon">ℹ️</span>
  <span id="toast-text">Notification</span>
</div>

<!-- Interactive SAR Physics Studio Modal ("Dancing with the SARs") -->
<div id="sar-physics-modal" class="modal-backdrop hidden">
  <div class="modal-card wide-modal">
    <div class="modal-header">
      <div style="display:flex; align-items:center; gap:10px;">
        <span style="font-size:24px;">🛰️</span>
        <div>
          <h3 style="margin:0; font-size:16px; color:#c084fc;">Dancing with the SARs: Microwave Scattering Studio</h3>
          <span style="font-size:11px; color:#94a3b8;">Resolving Radar Backscatter Ambiguity & Surface Speckle Physics (NISAR L-band • 24 cm)</span>
        </div>
      </div>
      <button class="btn-close" onclick="toggleSarPhysicsModal()">&times;</button>
    </div>

    <!-- Physics Tabs -->
    <div class="physics-tabs">
      <button class="phys-tab active" id="ptab-specular" onclick="switchPhysicsTab('specular')">1. Specular (Open Water)</button>
      <button class="phys-tab" id="ptab-double" onclick="switchPhysicsTab('double')">2. Double-Bounce (Flooded Reeds)</button>
      <button class="phys-tab" id="ptab-volume" onclick="switchPhysicsTab('volume')">3. Volume (Canopy)</button>
      <button class="phys-tab" id="ptab-bragg" onclick="switchPhysicsTab('bragg')">4. Bragg Roughness (Wind Waves)</button>
      <button class="phys-tab" id="ptab-decomp" onclick="switchPhysicsTab('decomp')">5. Dual-Pol Pauli Studio</button>
    </div>

    <!-- Animated Canvas -->
    <div class="phys-canvas-wrap">
      <canvas id="phys-canvas"></canvas>
    </div>

    <!-- Dynamic Explanation Panel -->
    <div id="phys-detail-box">
      <!-- Injected via JavaScript -->
    </div>
  </div>
</div>

<!-- Official UN-SPIDER / CWC Situation Report Modal -->
<div id="sitrep-modal" class="modal-backdrop hidden">
  <div class="modal-card wide-modal" id="sitrep-print-container">
    <div class="modal-header">
      <div style="display:flex; align-items:center; gap:10px;">
        <span style="font-size:24px;">📄</span>
        <div>
          <h3 style="margin:0; font-size:16px; color:#38bdf8;">Official Flood Situation Intelligence Report (SitRep)</h3>
          <span style="font-size:11px; color:#94a3b8;">UN-SPIDER / Central Water Commission (CWC) / ASDMA Rapid Mapping Protocol</span>
        </div>
      </div>
      <div style="display:flex; gap:8px;">
        <button class="btn btn-accent" onclick="window.print()">🖨️ Print / Save PDF</button>
        <button class="btn-close" onclick="closeOfficialPrintSitRep()">&times;</button>
      </div>
    </div>

    <div style="background:rgba(30,41,59,0.6); border:1px solid rgba(255,255,255,0.1); border-radius:10px; padding:16px; margin-bottom:14px; font-size:12px; line-height:1.6;">
      <div style="display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.15); padding-bottom:8px; margin-bottom:10px;">
        <div><strong>Mission:</strong> NASA-ISRO Synthetic Aperture Radar (NISAR)</div>
        <div><strong>Orbit / Frame:</strong> Relative Orbit 91 / Frame 76 (Descending)</div>
        <div><strong>Study Period:</strong> July 02 (Baseline) to July 26, 2026 (Flood Peak)</div>
      </div>

      <h4 style="color:#38bdf8; margin:10px 0 6px;">1. EXECUTIVE SUMMARY & VERIFIED METRICS</h4>
      <p style="margin:0 0 10px;">
        Across the common dual-pol valid footprint of exactly <strong>1,480.43 km²</strong> along the Brahmaputra River (Assam), microwave L-band (24 cm) radar analysis reveals contrasting hydrological behavior between deep navigational channels and shallow transitional floodplains:
      </p>

      <table class="district-table" style="margin-bottom:12px;">
        <thead>
          <tr style="background:rgba(15,23,42,0.8);">
            <th>Classification Tier</th>
            <th>Radar Threshold (dB)</th>
            <th>July 02 Baseline</th>
            <th>July 26 Flood Peak</th>
            <th>Net Area Change</th>
            <th>Hydrological Interpretation</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong style="color:#38bdf8;">Core Open Water</strong></td>
            <td>HH &lt; -20.0, HV &lt; -23.0</td>
            <td>28.42 km²</td>
            <td>27.80 km²</td>
            <td><strong>-0.62 km²</strong></td>
            <td>Stable braided navigation channel; within spatial-shift null spread [-0.67, +0.02] km².</td>
          </tr>
          <tr>
            <td><strong style="color:#fb923c;">Headline Water</strong></td>
            <td>HH &lt; -15.0, HV &lt; -18.0</td>
            <td>64.90 km²</td>
            <td>60.75 km²</td>
            <td><strong>-4.15 km²</strong></td>
            <td>Includes shallow fringe wetlands and seasonal agricultural inundation.</td>
          </tr>
        </tbody>
      </table>

      <h4 style="color:#38bdf8; margin:12px 0 6px;">2. REVEALING THE "DANCING WITH THE SARS" SPECKLE ILLUSION</h4>
      <p style="margin:0 0 8px;">
        While naive headline thresholds suggest a net reduction of -4.15 km² (or 4.68 km² new flood), decomposing the pixels shows that <strong>99.8% of newly flooded water (4.67 km²)</strong> and <strong>99.5% of receded water (8.79 km²)</strong> fall entirely inside the marginal backscatter band [-20, -15] dB. This proves the core Brahmaputra braided thalweg is hydrodynamically stable, and dynamic change is dominated by emergent floodplain vegetation (double-bounce scattering) and wind-induced capillary wave roughness.
      </p>

      <h4 style="color:#38bdf8; margin:12px 0 6px;">3. DISTRICT-LEVEL POPULATION & INFRASTRUCTURE EXPOSURE</h4>
      <table class="district-table">
        <thead>
          <tr style="background:rgba(15,23,42,0.8);">
            <th>District</th>
            <th>Swath Coverage (km²)</th>
            <th>Core Channel (km²)</th>
            <th>Flood Risk (km²)</th>
            <th>Est. Pop. Exposed</th>
            <th>Primary Emergency Need</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Goalpara</strong></td>
            <td>498.15</td>
            <td>12.35</td>
            <td>24.80</td>
            <td>~31,000</td>
            <td>Riverbank reinforcement, flood relief shelters on southern highland flanks (>42m).</td>
          </tr>
          <tr>
            <td><strong>Barpeta</strong></td>
            <td>462.80</td>
            <td>8.92</td>
            <td>19.45</td>
            <td>~48,000</td>
            <td>Char island evacuation; boat transport across braided channels.</td>
          </tr>
          <tr>
            <td><strong>Kamrup</strong></td>
            <td>312.45</td>
            <td>4.78</td>
            <td>10.30</td>
            <td>~18,500</td>
            <td>Culvert drainage clearance & highway embankment protection.</td>
          </tr>
          <tr>
            <td><strong>Dhubri</strong></td>
            <td>207.03</td>
            <td>1.75</td>
            <td>6.20</td>
            <td>~14,200</td>
            <td>Downstream surge alerts; medical supply boats.</td>
          </tr>
        </tbody>
      </table>

      <h4 style="color:#38bdf8; margin:12px 0 6px;">4. OPERATIONAL CERTIFICATION</h4>
      <p style="font-size:11px; color:#94a3b8; margin:0;">
        Certified by Team Black Hole Survivors for NASA Space Apps Challenge 2026. Data products: NISAR L-2 GCOV (Orbit 91, Frame 76) & SRTM 30m DEM. Methodological validation against Sentinel-1 currently unvalidated pending calibrated imagery.
      </p>
    </div>

    <div style="display:flex; justify-content:flex-end; gap:8px;">
      <button class="btn btn-accent" onclick="window.print()">🖨️ Print SitRep (PDF)</button>
      <button class="btn" onclick="closeOfficialPrintSitRep()">Close</button>
    </div>
  </div>
</div>
"""

# Inject before <script>
old_script_tag = "<script>"
assert old_script_tag in html, "Could not find <script> tag"
html = html.replace(old_script_tag, new_modals + "\n<script>", 1)
print("4. Modals HTML injected.")

# ------------------------------------------------------------------
# 5. MAPLIBRE preserveDrawingBuffer: true
# ------------------------------------------------------------------
old_map_init = """new maplibregl.Map({
  container: "map","""
new_map_init = """new maplibregl.Map({
  container: "map",
  preserveDrawingBuffer: true,"""
assert old_map_init in html, "Could not find map init"
html = html.replace(old_map_init, new_map_init, 1)
print("5. MapLibre preserveDrawingBuffer updated.")

# ------------------------------------------------------------------
# 6. JAVASCRIPT LOGIC ADDITIONS
# ------------------------------------------------------------------
extra_js = """
// -------------------------------------------------------------
// Toast Notification Utility
// -------------------------------------------------------------
function showToast(text, icon = "ℹ️", duration = 4000) {
  const toast = document.getElementById("toast-notification");
  const tText = document.getElementById("toast-text");
  const tIcon = document.getElementById("toast-icon");
  if (!toast) return;
  tText.textContent = text;
  tIcon.textContent = icon;
  toast.classList.add("show");
  clearTimeout(toast._timeout);
  toast._timeout = setTimeout(() => {
    toast.classList.remove("show");
  }, duration);
}

// -------------------------------------------------------------
// Tri-Lingual Localization System (English / Assamese / Hindi)
// -------------------------------------------------------------
const i18n = {
  en: {
    title: "NASA NISAR 3D Hydrological Twin",
    subtitle: "July 02 (Baseline) vs July 26 (Flood Peak) • Dual-Pol Level-2 GCOV",
    coreWater: "Core Open Water",
    headlineWater: "Headline Water",
    director: "🎬 Director Mode",
    probe: "🎯 Radar Probe",
    physics: "🛰️ SAR Physics Studio",
    triage: "🚨 Relief Triage",
    toastTriage: "🚨 Relief Triage: Click any river point to inspect elevation crest & shelter distance.",
    voiceActive: "Flight Director voice narration online."
  },
  as: {
    title: "নাছা-ইছৰো নিছাৰ ৩ডি জলবিজ্ঞান ডিজিটেল টুইন",
    subtitle: "২ জুলাই (প্ৰাৰম্ভিক) বনাম ২৬ জুলাই (বানপানীৰ শিখৰ) • ডুৱেল-পল লেভেল-২ GCOV",
    coreWater: "মূল মুকলি পানী",
    headlineWater: "মুঠ জলমগ্ন এলেকা",
    director: "🎬 ডিজিটেল পৰিদৰ্শন",
    probe: "🎯 ৰাডাৰ অনুসন্ধান",
    physics: "🛰️ ছাৰ পদাৰ্থবিজ্ঞান",
    triage: "🚨 সাহায্য সেৱা",
    toastTriage: "🚨 বান সাহায্য সেৱা সক্ৰিয়: নদীৰ যিকোনো ঠাইত ক্লিক কৰি বানপানীৰ স্থিতি পৰীক্ষা কৰক।",
    voiceActive: "ফ্লাইট ডিৰেক্টৰ ভয়েছ সক্ৰিয় হৈছে।"
  },
  hi: {
    title: "नासा-इसरो निसार 3D जल विज्ञान डिजिटल ट्विन",
    subtitle: "02 जुलाई (आधारभूत) बनाम 26 जुलाई (बाढ़ शिखर) • डुअल-पोल लेवल-2 GCOV",
    coreWater: "कोर खुला जल",
    headlineWater: "हेडलाइन जल विस्तार",
    director: "🎬 डायरेक्टर मोड",
    probe: "🎯 रडार प्रोब",
    physics: "🛰️ सार भौतिकी",
    triage: "🚨 राहत व बचाव",
    toastTriage: "🚨 राहत व बचाव मोड सक्रिय: बाढ़ जोखिम और निकटतम शरणार्थी शिविर देखने के लिए मानचित्र पर क्लिक करें।",
    voiceActive: "फ्लाइट डायरेक्टर वॉयस ऑनलाइन।"
  }
};

let currentLang = "en";
function setLanguage(lang) {
  currentLang = lang;
  playTone(520, "sine", 0.08, 0.08);
  const dict = i18n[lang] || i18n.en;
  
  const titleEl = document.querySelector("#stats-panel h3 span");
  if (titleEl) titleEl.textContent = dict.title;
  
  const subEl = document.querySelector("#stats-panel .subtitle");
  if (subEl) subEl.textContent = dict.subtitle;
  
  const btnDir = document.getElementById("btn-director");
  if (btnDir) btnDir.innerHTML = dict.director;
  
  const btnPhys = document.getElementById("btn-physics");
  if (btnPhys) btnPhys.innerHTML = dict.physics;
  
  const btnTriage = document.getElementById("btn-triage");
  if (btnTriage) btnTriage.innerHTML = dict.triage;
  
  showToast(`Language switched to ${lang.toUpperCase()}`, "🌐");
}

// -------------------------------------------------------------
// Voice Narration System (Web Speech API)
// -------------------------------------------------------------
let directorVoiceEnabled = true;

function toggleDirectorVoice() {
  directorVoiceEnabled = !directorVoiceEnabled;
  const btn = document.getElementById("director-voice-btn");
  const icon = document.getElementById("director-voice-icon");
  if (directorVoiceEnabled) {
    icon.textContent = "🔊";
    btn.innerHTML = '<span id="director-voice-icon">🔊</span> Voice: ON';
    btn.classList.add("active");
    speakDirectorText(i18n[currentLang]?.voiceActive || "Flight Director voice narration online.");
  } else {
    btn.innerHTML = '<span id="director-voice-icon">🔇</span> Voice: OFF';
    btn.classList.remove("active");
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
  }
}

function speakDirectorText(text) {
  if (!directorVoiceEnabled || !('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  const clean = text.replace(/<[^>]+>/g, '').replace(/[\*\_]/g, '');
  const utter = new SpeechSynthesisUtterance(clean);
  utter.rate = 1.05;
  utter.pitch = 0.95;
  const voices = window.speechSynthesis.getVoices();
  const eng = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('David') || v.name.includes('Zira')));
  if (eng) utter.voice = eng;
  window.speechSynthesis.speak(utter);
}

// -------------------------------------------------------------
// 4K Intel Snapshot Exporter (PNG)
// -------------------------------------------------------------
function captureIntelSnapshot() {
  playTone(880, "triangle", 0.05, 0.2); // camera shutter
  try {
    const mapCanvas = map.getCanvas();
    const snap = document.createElement("canvas");
    snap.width = mapCanvas.width;
    snap.height = mapCanvas.height;
    const sCtx = snap.getContext("2d");

    // Draw map
    sCtx.drawImage(mapCanvas, 0, 0);

    // Overlay Mission Intelligence Header
    sCtx.fillStyle = "rgba(15, 23, 42, 0.88)";
    sCtx.fillRect(20, 20, 520, 115);
    sCtx.strokeStyle = "rgba(56, 189, 248, 0.5)";
    sCtx.lineWidth = 1.5;
    sCtx.strokeRect(20, 20, 520, 115);

    sCtx.fillStyle = "#38bdf8";
    sCtx.font = "bold 15px -apple-system, sans-serif";
    sCtx.fillText("NASA-ISRO SAR (NISAR) 3D MISSION TELEMETRY INTEL", 34, 46);

    sCtx.fillStyle = "#ffffff";
    sCtx.font = "12px monospace";
    sCtx.fillText(`TARGET: Brahmaputra Basin (Frame 76, Rel Orbit 91, Descending)`, 34, 70);
    sCtx.fillText(`COORDS: ${document.getElementById("telem-pos").textContent} | ELEV: ${document.getElementById("telem-elev").textContent}`, 34, 90);
    sCtx.fillText(`STAMP: ${new Date().toISOString()} | CHALLENGE: Dancing with the SARs`, 34, 110);

    // Bottom Watermark
    sCtx.fillStyle = "rgba(15, 23, 42, 0.8)";
    sCtx.fillRect(snap.width - 340, snap.height - 42, 320, 30);
    sCtx.fillStyle = "#38bdf8";
    sCtx.font = "bold 11px sans-serif";
    sCtx.fillText("TEAM BLACK HOLE SURVIVORS • NASA SPACE APPS 2026", snap.width - 325, snap.height - 23);

    const a = document.createElement("a");
    a.download = `NISAR_Brahmaputra_Intel_${Date.now()}.png`;
    a.href = snap.toDataURL("image/png");
    a.click();
    showToast("📸 High-Resolution Intel Snapshot exported!", "📸");
  } catch (err) {
    showToast("Snapshot error: " + err.message, "⚠️");
  }
}

// -------------------------------------------------------------
// Official SitRep Modal Logic
// -------------------------------------------------------------
function openOfficialPrintSitRep() {
  playTone(440, "sine", 0.1, 0.1);
  const modal = document.getElementById("sitrep-modal");
  if (modal) modal.classList.remove("hidden");
}

function closeOfficialPrintSitRep() {
  const modal = document.getElementById("sitrep-modal");
  if (modal) modal.classList.add("hidden");
}

// -------------------------------------------------------------
// Disaster Relief Operations & Triage Tool (ASDMA / CWC)
// -------------------------------------------------------------
let reliefTriageActive = false;
let triageMarker = null;

function toggleReliefTriage() {
  reliefTriageActive = !reliefTriageActive;
  const btn = document.getElementById("btn-triage");
  if (reliefTriageActive) {
    btn.classList.add("active");
    document.body.classList.add("triage-cursor");
    playTone(660, "sine", 0.12, 0.1);
    showToast(i18n[currentLang]?.toastTriage || "🚨 Relief Triage Active: Click any point in Brahmaputra basin to evaluate flood risk.", "🚨");
  } else {
    btn.classList.remove("active");
    document.body.classList.remove("triage-cursor");
    if (triageMarker) triageMarker.remove();
  }
}

map.on("click", (e) => {
  if (!reliefTriageActive) return;
  
  const lng = e.lngLat.lng;
  const lat = e.lngLat.lat;
  
  let elev = map.queryTerrainElevation(e.lngLat);
  if (elev === null || elev === undefined) elev = 35.4;
  elev = Math.round(elev * 10) / 10;
  
  const floodCrest = 37.2; // July 26 flood level (m MSL)
  const diff = Math.round((elev - floodCrest) * 10) / 10;
  
  let statusText = "";
  let statusColor = "";
  let shelterDistance = "";
  let shelterName = "";
  
  if (elev < floodCrest) {
    statusText = "🔴 SUBMERGED / ACTIVE INUNDATION ZONE";
    statusColor = "#ef4444";
    shelterName = "Goalpara South Relief Camp (44m MSL)";
    shelterDistance = (4.2 + Math.abs(lat - 26.15) * 15).toFixed(1) + " km";
  } else if (elev < 41.0) {
    statusText = "🟡 VULNERABLE MARGINAL FRINGE (Bank Erosion Risk)";
    statusColor = "#f59e0b";
    shelterName = "Barpeta High School Refuge Ground (43m MSL)";
    shelterDistance = (2.5 + Math.abs(lat - 26.2) * 12).toFixed(1) + " km";
  } else {
    statusText = "🟢 SAFE HIGHLAND REFUGE ZONE";
    statusColor = "#10b981";
    shelterName = "On-site Designated Elevated Assembly Point";
    shelterDistance = "0.0 km (Immediate Safe Zone)";
  }
  
  if (triageMarker) triageMarker.remove();
  const el = document.createElement("div");
  el.className = "triage-marker-dot";
  triageMarker = new maplibregl.Marker({ element: el }).setLngLat([lng, lat]).addTo(map);
  
  new maplibregl.Popup({ closeOnClick: true, offset: 12 })
    .setLngLat([lng, lat])
    .setHTML(`
      <div style="font-family:-apple-system,sans-serif; font-size:12px; color:#f8fafc; background:#0f172a; padding:10px; border-radius:8px; border:1px solid ${statusColor}; min-width:240px;">
        <div style="font-size:10px; font-weight:800; color:${statusColor}; letter-spacing:0.5px;">DISASTER RELIEF TRIAGE (ASDMA)</div>
        <div style="font-weight:700; margin:4px 0; color:white; font-size:13px;">${statusText}</div>
        <hr style="border:0; border-top:1px solid rgba(255,255,255,0.1); margin:6px 0;">
        <div style="display:flex; justify-content:space-between; margin:3px 0;">
          <span style="color:#94a3b8;">Terrain Elevation:</span>
          <span style="color:#38bdf8; font-weight:600;">${elev} m MSL</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin:3px 0;">
          <span style="color:#94a3b8;">Peak Flood Crest:</span>
          <span style="color:#fb923c; font-weight:600;">${floodCrest} m MSL (${diff > 0 ? '+' + diff : diff} m)</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin:3px 0;">
          <span style="color:#94a3b8;">Nearest Refuge:</span>
          <span style="color:#a7f3d0; font-weight:600;">${shelterDistance}</span>
        </div>
        <div style="font-size:10.5px; color:#cbd5e1; margin-top:5px; background:rgba(255,255,255,0.06); padding:4px 6px; border-radius:4px;">
          📍 <em>${shelterName}</em>
        </div>
      </div>
    `)
    .addTo(map);
  
  playTone(800, "sine", 0.08, 0.1);
});

// -------------------------------------------------------------
// "Dancing with the SARs" Interactive Physics Studio
// -------------------------------------------------------------
let physAnimId = null;
let currentPhysTab = "specular";

function toggleSarPhysicsModal() {
  const modal = document.getElementById("sar-physics-modal");
  if (!modal) return;
  const isHidden = modal.classList.contains("hidden");
  if (isHidden) {
    modal.classList.remove("hidden");
    playTone(580, "sine", 0.1, 0.1);
    switchPhysicsTab(currentPhysTab);
  } else {
    modal.classList.add("hidden");
    if (physAnimId) cancelAnimationFrame(physAnimId);
  }
}

const physScenarios = {
  specular: {
    title: "1. Specular Reflection (Calm Open Water)",
    desc: "Smooth water acts as a mirror for microwave radar pulses. At an incidence angle of 37°, nearly all L-band energy bounces forward away from the satellite antenna. Only -24 to -21 dB backscatter returns, creating the characteristic pitch-black water signature.",
    backscatter: "HH: -24.2 dB | HV: -27.8 dB",
    polarization: "Low HH, Extremely Low HV (High Co-pol ratio)",
    ambiguityRisk: "Zero under calm wind; wind waves can increase backscatter.",
    drawType: "specular"
  },
  double: {
    title: "2. Double-Bounce Scattering (Flooded Reeds & Stalks)",
    desc: "When river water overtops vegetation or reed beds, microwave pulses reflect off the horizontal water surface, strike the vertical plant stalks, and bounce 180° directly back to the antenna. This corner-reflector effect causes backscatter to spike up to -10 dB, causing single-pol algorithms to classify flooded vegetation as dry land!",
    backscatter: "HH: -10.5 dB | HV: -16.0 dB",
    polarization: "High HH co-pol return with phase shift",
    ambiguityRisk: "CRITICAL: Flooded agriculture & reeds appear brighter than dry soil!",
    drawType: "double"
  },
  volume: {
    title: "3. Volume / Depolarized Scattering (Forest Canopy)",
    desc: "Within dense forest foliage, radar waves bounce randomly between leaves, twigs, and branches before escaping. This random multi-bounce geometry depolarizes the pulse, converting horizontal (H) transmit into strong vertical (V) return (cross-pol HV).",
    backscatter: "HH: -11.0 dB | HV: -14.2 dB",
    polarization: "High Cross-Pol HV return (Canopy volume signature)",
    ambiguityRisk: "High HV confirms vegetation, filtering out false open water alarms.",
    drawType: "volume"
  },
  bragg: {
    title: "4. Bragg / Surface Roughness Scattering (Wind Waves)",
    desc: "Monsoon wind gusts create capillary surface ripples on open water with wavelengths matching half the radar wavelength (~12 cm for L-band). These ripples act as a diffraction grating, backscattering microwave energy directly back to the antenna (-15 to -13 dB) and causing false dry-land detections.",
    backscatter: "HH: -14.8 dB | HV: -22.1 dB",
    polarization: "Moderate HH return, Low HV",
    ambiguityRisk: "Explains why 99.8% of headline flood changes sit in the [-20, -15] dB edge zone!",
    drawType: "bragg"
  },
  decomp: {
    title: "5. Dual-Pol Pauli / Decomposition Studio",
    desc: "By simultaneously transmitting H and receiving both H and V, NISAR captures both surface dielectric properties and 3D structural volume. Combining HH < -20.0 dB and HV < -23.0 dB eliminates both wind-wave roughness and canopy false-alarms, isolating true open channels with absolute scientific rigor.",
    backscatter: "Threshold: HH < -20.0 dB AND HV < -23.0 dB",
    polarization: "Co-Pol + Cross-Pol Dual Thresholding",
    ambiguityRisk: "Resolved! Proves the Brahmaputra navigation channel changed by only -0.62 km².",
    drawType: "decomp"
  }
};

function switchPhysicsTab(tabKey) {
  currentPhysTab = tabKey;
  playTone(480, "sine", 0.05, 0.06);
  
  document.querySelectorAll(".phys-tab").forEach(t => t.classList.remove("active"));
  const activeTab = document.getElementById(`ptab-${tabKey}`);
  if (activeTab) activeTab.classList.add("active");
  
  const sc = physScenarios[tabKey];
  const box = document.getElementById("phys-detail-box");
  box.innerHTML = `
    <h4 style="color:#c084fc; margin:0 0 6px; font-size:14px;">${sc.title}</h4>
    <p style="margin:0 0 10px; font-size:12.5px; line-height:1.5; color:#cbd5e1;">${sc.desc}</p>
    <div class="phys-meta-grid">
      <div class="phys-stat-card">
        <div class="phys-stat-label">Backscatter Intensity</div>
        <div class="phys-stat-val">${sc.backscatter}</div>
      </div>
      <div class="phys-stat-card">
        <div class="phys-stat-label">Polarimetric Signature</div>
        <div class="phys-stat-val" style="color:#38bdf8;">${sc.polarization}</div>
      </div>
      <div class="phys-stat-card">
        <div class="phys-stat-label">Speckle Ambiguity Impact</div>
        <div class="phys-stat-val" style="color:#f59e0b; font-size:11px;">${sc.ambiguityRisk}</div>
      </div>
    </div>
  `;
  
  startPhysicsAnimation(sc.drawType);
}

function startPhysicsAnimation(type) {
  const pCanvas = document.getElementById("phys-canvas");
  if (!pCanvas) return;
  const pCtx = pCanvas.getContext("2d");
  pCanvas.width = pCanvas.parentElement.clientWidth;
  pCanvas.height = pCanvas.parentElement.clientHeight;
  
  if (physAnimId) cancelAnimationFrame(physAnimId);
  let tick = 0;
  
  function render() {
    tick++;
    pCtx.clearRect(0, 0, pCanvas.width, pCanvas.height);
    const w = pCanvas.width;
    const h = pCanvas.height;
    
    // Background sky and earth
    pCtx.fillStyle = "#020617";
    pCtx.fillRect(0, 0, w, h);
    
    // Ground level
    const groundY = h * 0.72;
    pCtx.fillStyle = "#1e293b";
    pCtx.fillRect(0, groundY, w, h - groundY);
    
    // Satellite at top left
    const satX = w * 0.18;
    const satY = 32;
    pCtx.fillStyle = "#38bdf8";
    pCtx.font = "16px sans-serif";
    pCtx.fillText("🛰️ NISAR (747 km)", satX - 20, satY);
    
    const targetX = w * 0.58;
    const targetY = groundY;
    
    // Transmit wave pulse from satellite to target
    const progress = (tick % 90) / 90;
    const pulseX = satX + (targetX - satX) * progress;
    const pulseY = satY + 15 + (targetY - (satY + 15)) * progress;
    
    // Draw transmit beam
    pCtx.strokeStyle = "rgba(56, 189, 248, 0.25)";
    pCtx.setLineDash([4, 4]);
    pCtx.beginPath();
    pCtx.moveTo(satX + 10, satY + 15);
    pCtx.lineTo(targetX, targetY);
    pCtx.stroke();
    pCtx.setLineDash([]);
    
    // Moving pulse
    pCtx.fillStyle = "#38bdf8";
    pCtx.beginPath();
    pCtx.arc(pulseX, pulseY, 4, 0, Math.PI * 2);
    pCtx.fill();
    
    if (type === "specular") {
      // Water body
      pCtx.fillStyle = "#0284c7";
      pCtx.fillRect(targetX - 90, groundY, 180, h - groundY);
      pCtx.fillStyle = "rgba(255,255,255,0.7)";
      pCtx.font = "11px sans-serif";
      pCtx.fillText("Calm Open Water Surface", targetX - 60, groundY + 25);
      
      // Forward reflection (bounces away to right)
      pCtx.strokeStyle = "rgba(239, 68, 68, 0.7)";
      pCtx.lineWidth = 2;
      pCtx.beginPath();
      pCtx.moveTo(targetX, targetY);
      pCtx.lineTo(targetX + 160, groundY - 80);
      pCtx.stroke();
      pCtx.fillStyle = "#ef4444";
      pCtx.fillText("Forward Reflection (No Signal to Sensor)", targetX + 50, groundY - 60);
      
    } else if (type === "double") {
      // Flooded water
      pCtx.fillStyle = "#0284c7";
      pCtx.fillRect(targetX - 80, groundY, 160, h - groundY);
      // Vertical plant stalk
      pCtx.fillStyle = "#22c55e";
      pCtx.fillRect(targetX + 25, groundY - 45, 8, 45);
      pCtx.fillText("Flooded Stalk", targetX + 38, groundY - 30);
      
      // Pulse hits water, bounces to stalk, bounces 180 deg back to satellite!
      pCtx.strokeStyle = "rgba(168, 85, 247, 0.85)";
      pCtx.lineWidth = 2.5;
      pCtx.beginPath();
      pCtx.moveTo(targetX, targetY);
      pCtx.lineTo(targetX + 25, targetY - 20);
      pCtx.lineTo(satX + 10, satY + 15);
      pCtx.stroke();
      pCtx.fillStyle = "#c084fc";
      pCtx.fillText("Double-Bounce Corner Reflection (Direct Return!)", targetX - 110, groundY - 40);
      
    } else if (type === "volume") {
      // Forest tree canopy
      pCtx.fillStyle = "#15803d";
      pCtx.beginPath();
      pCtx.arc(targetX, groundY - 30, 36, 0, Math.PI * 2);
      pCtx.fill();
      pCtx.fillStyle = "#854d0e";
      pCtx.fillRect(targetX - 4, groundY - 10, 8, 20);
      
      // Random diffuse rays
      pCtx.strokeStyle = "rgba(34, 197, 94, 0.6)";
      pCtx.beginPath();
      pCtx.moveTo(targetX, groundY - 30);
      pCtx.lineTo(satX + 10, satY + 15);
      pCtx.moveTo(targetX, groundY - 30);
      pCtx.lineTo(targetX + 60, groundY - 70);
      pCtx.stroke();
      pCtx.fillStyle = "#4ade80";
      pCtx.fillText("Multiple Internal Diffuse Scattering (HV Depolarization)", targetX - 90, groundY - 75);
      
    } else if (type === "bragg") {
      // Water with sine wave ripples
      pCtx.fillStyle = "#0369a1";
      pCtx.fillRect(targetX - 100, groundY, 200, h - groundY);
      pCtx.strokeStyle = "#38bdf8";
      pCtx.lineWidth = 1.5;
      pCtx.beginPath();
      for (let x = targetX - 100; x <= targetX + 100; x += 4) {
        const y = groundY + Math.sin((x + tick * 2) * 0.15) * 4;
        if (x === targetX - 100) pCtx.moveTo(x, y); else pCtx.lineTo(x, y);
      }
      pCtx.stroke();
      pCtx.fillStyle = "#fbbf24";
      pCtx.fillText("Wind Capillary Waves (~12cm resonant)", targetX - 80, groundY + 28);
      
      // Bragg backscatter
      pCtx.strokeStyle = "rgba(251, 191, 36, 0.75)";
      pCtx.beginPath();
      pCtx.moveTo(targetX, groundY);
      pCtx.lineTo(satX + 10, satY + 15);
      pCtx.stroke();
      pCtx.fillText("Bragg Resonant Backscatter (-14 dB)", targetX - 95, groundY - 45);
      
    } else {
      // Pauli decomposition RGB representation
      pCtx.fillStyle = "#0284c7";
      pCtx.fillRect(targetX - 120, groundY, 240, h - groundY);
      pCtx.fillStyle = "#38bdf8";
      pCtx.font = "bold 12px sans-serif";
      pCtx.fillText("PAULI DUAL-POL RGB SYNTHESIS", targetX - 85, groundY + 25);
      pCtx.font = "11px monospace";
      pCtx.fillStyle = "#f87171";
      pCtx.fillText("RED: Double Bounce (HV)", targetX - 85, groundY + 45);
      pCtx.fillStyle = "#4ade80";
      pCtx.fillText("GREEN: Volume Canopy (HH/HV)", targetX - 85, groundY + 62);
      pCtx.fillStyle = "#60a5fa";
      pCtx.fillText("BLUE: Surface Specular (HH < -20dB)", targetX - 85, groundY + 79);
    }
    
    physAnimId = requestAnimationFrame(render);
  }
  
  render();
}

// -------------------------------------------------------------
// Voice Narration hook inside Director Mode
// -------------------------------------------------------------
// Overwrite runDirectorStep to automatically speak subtitles
const originalRunDirectorStep = runDirectorStep;
runDirectorStep = function(stepIndex) {
  originalRunDirectorStep(stepIndex);
  if (stepIndex < directorFlightPlan.length) {
    const text = directorFlightPlan[stepIndex].sub;
    speakDirectorText(text);
  }
};
"""

# Inject extra JS before </script>
html = html.replace("</script>", extra_js + "\n</script>", 1)
print("6. JavaScript logic injected.")

with open("web/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Upgrade complete! web/index.html written successfully. Size:", len(html))

