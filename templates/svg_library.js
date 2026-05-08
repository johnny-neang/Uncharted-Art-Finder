const SVG = {};

/* --- 1. Bryan Valenzuela --- text-figure / glass orbs --- */
SVG.valenzuela_text = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bv1" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#F2E9D8"/><stop offset="1" stop-color="#D9C8A8"/>
    </linearGradient>
    <pattern id="textPat" width="3" height="2" patternUnits="userSpaceOnUse">
      <path d="M0 1 L3 1" stroke="#1A1D24" stroke-width="0.4" opacity="0.55"/>
    </pattern>
  </defs>
  <rect width="400" height="300" fill="url(#bv1)"/>
  <!-- silhouette of woman reading -->
  <g>
    <path d="M120 280 Q110 220 130 180 Q115 145 145 120 Q150 90 175 85 Q205 75 225 100 Q245 115 240 145 Q260 165 250 195 Q280 215 275 250 Q280 280 280 300 L120 300 Z"
          fill="url(#textPat)" opacity="0.95"/>
    <!-- pen lines suggesting text -->
    <g stroke="#1A1D24" stroke-width="0.3" opacity="0.6" fill="none">
      <path d="M140 130 Q165 128 195 132"/><path d="M138 145 Q170 143 205 147"/>
      <path d="M140 160 Q175 158 215 162"/><path d="M145 178 Q180 176 225 180"/>
      <path d="M150 198 Q185 196 230 200"/><path d="M155 218 Q190 216 235 220"/>
      <path d="M160 238 Q195 236 240 240"/><path d="M165 258 Q200 256 245 260"/>
    </g>
    <!-- hint of a book -->
    <path d="M180 200 L235 195 L240 220 L185 225 Z" fill="#1A1D24" opacity="0.18"/>
    <line x1="207" y1="198" x2="212" y2="222" stroke="#F2E9D8" stroke-width="1"/>
  </g>
  <!-- accent thread -->
  <path d="M40 60 Q120 80 200 50 Q280 30 360 70" stroke="#B68A3F" stroke-width="1" fill="none" opacity="0.8"/>
  <path d="M40 240 Q120 260 200 230 Q280 210 360 240" stroke="#466F95" stroke-width="1" fill="none" opacity="0.6"/>
</svg>`;

SVG.valenzuela_orbs = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bv2bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#142838"/><stop offset="1" stop-color="#2C4A68"/>
    </linearGradient>
    <radialGradient id="orb1" cx="0.35" cy="0.35"><stop offset="0" stop-color="#fff" stop-opacity="0.9"/><stop offset="0.4" stop-color="#88A8C7" stop-opacity="0.4"/><stop offset="1" stop-color="#142838" stop-opacity="0"/></radialGradient>
    <radialGradient id="orb2" cx="0.4" cy="0.3"><stop offset="0" stop-color="#fff" stop-opacity="0.85"/><stop offset="0.5" stop-color="#E0C588" stop-opacity="0.35"/><stop offset="1" stop-color="#142838" stop-opacity="0"/></radialGradient>
  </defs>
  <rect width="400" height="300" fill="url(#bv2bg)"/>
  <!-- vertical text columns -->
  <g stroke="#88A8C7" stroke-width="0.3" fill="none" opacity="0.4">
    <path d="M30 30 Q30 150 30 270"/><path d="M55 30 Q55 150 55 270"/>
    <path d="M345 30 Q345 150 345 270"/><path d="M370 30 Q370 150 370 270"/>
  </g>
  <!-- glass spheres -->
  <circle cx="100" cy="120" r="52" fill="url(#orb1)" opacity="0.9"/>
  <circle cx="100" cy="120" r="52" fill="none" stroke="#fff" stroke-width="0.4" opacity="0.4"/>
  <circle cx="220" cy="180" r="68" fill="url(#orb2)" opacity="0.85"/>
  <circle cx="220" cy="180" r="68" fill="none" stroke="#E0C588" stroke-width="0.4" opacity="0.4"/>
  <circle cx="320" cy="100" r="38" fill="url(#orb1)" opacity="0.85"/>
  <circle cx="320" cy="100" r="38" fill="none" stroke="#fff" stroke-width="0.4" opacity="0.4"/>
  <circle cx="160" cy="240" r="28" fill="url(#orb2)" opacity="0.7"/>
  <!-- reflection highlights -->
  <ellipse cx="84" cy="100" rx="10" ry="6" fill="#fff" opacity="0.5"/>
  <ellipse cx="200" cy="160" rx="12" ry="8" fill="#fff" opacity="0.5"/>
  <ellipse cx="308" cy="88" rx="6" ry="4" fill="#fff" opacity="0.45"/>
</svg>`;

/* --- 2. Maren Conrad --- koi / portrait --- */
SVG.conrad_koi = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="mc1" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0E2438"/><stop offset="0.5" stop-color="#1B3A5C"/><stop offset="1" stop-color="#08172A"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#mc1)"/>
  <!-- ripples -->
  <g stroke="#88A8C7" stroke-width="0.5" fill="none" opacity="0.35">
    <ellipse cx="200" cy="150" rx="160" ry="90"/>
    <ellipse cx="200" cy="150" rx="120" ry="65"/>
    <ellipse cx="200" cy="150" rx="80" ry="42"/>
    <ellipse cx="320" cy="220" rx="60" ry="32"/>
    <ellipse cx="320" cy="220" rx="35" ry="18"/>
    <ellipse cx="80" cy="80" rx="40" ry="22"/>
  </g>
  <!-- koi 1 (orange/white) -->
  <g transform="translate(110 130) rotate(-12)">
    <path d="M0 0 Q40 -25 90 -10 Q120 0 130 8 Q120 14 110 22 Q100 28 90 25 Q40 30 0 0Z" fill="#F5F1EA"/>
    <path d="M-12 -2 Q-22 -10 -28 0 Q-22 8 -12 -2Z" fill="#F5F1EA"/>
    <path d="M125 -2 L150 -12 L155 0 L150 12 L125 4Z" fill="#F5F1EA"/>
    <!-- orange spots -->
    <ellipse cx="30" cy="-5" rx="22" ry="10" fill="#E0904A"/>
    <ellipse cx="80" cy="6" rx="18" ry="8" fill="#E0904A"/>
    <ellipse cx="60" cy="14" rx="10" ry="5" fill="#B45A3F"/>
    <!-- eye -->
    <circle cx="105" cy="-2" r="2" fill="#1A1D24"/>
  </g>
  <!-- koi 2 (red/black) -->
  <g transform="translate(220 200) rotate(20)">
    <path d="M0 0 Q40 -22 86 -8 Q116 2 124 8 Q116 14 102 20 Q86 25 60 22 Q30 18 0 0Z" fill="#F5F1EA"/>
    <path d="M-10 -2 Q-20 -8 -24 1 Q-20 8 -10 -2Z" fill="#F5F1EA"/>
    <path d="M120 -1 L142 -10 L146 2 L142 12 L120 5Z" fill="#F5F1EA"/>
    <ellipse cx="34" cy="-3" rx="20" ry="9" fill="#B45A3F"/>
    <ellipse cx="76" cy="4" rx="14" ry="6" fill="#1A1D24"/>
    <ellipse cx="58" cy="13" rx="8" ry="4" fill="#E0904A"/>
    <circle cx="100" cy="-2" r="2" fill="#1A1D24"/>
  </g>
  <!-- bubbles -->
  <g fill="#88A8C7" opacity="0.6">
    <circle cx="60" cy="60" r="3"/><circle cx="76" cy="48" r="2"/>
    <circle cx="350" cy="100" r="2.5"/><circle cx="365" cy="80" r="1.5"/>
  </g>
</svg>`;

SVG.conrad_ladybird = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="lb1" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FBF1DC"/><stop offset="1" stop-color="#E2C994"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#lb1)"/>
  <!-- dandelion abstraction (Lady Bird wildflower theme) -->
  <g transform="translate(200 160)">
    <!-- center -->
    <circle r="20" fill="#B68A3F"/>
    <!-- seed rays -->
    <g stroke="#fff" stroke-width="1.4" stroke-linecap="round">
      <g opacity="0.95">
        ${(() => { let s=''; for (let i=0;i<36;i++){ const a=i*10*Math.PI/180; const r1=22, r2=80+Math.random()*15; s+=`<line x1="${(r1*Math.cos(a)).toFixed(1)}" y1="${(r1*Math.sin(a)).toFixed(1)}" x2="${(r2*Math.cos(a)).toFixed(1)}" y2="${(r2*Math.sin(a)).toFixed(1)}"/>`; } return s; })()}
      </g>
    </g>
    <!-- floating seeds -->
    <g fill="#fff" opacity="0.9">
      <circle cx="120" cy="-40" r="3"/><circle cx="-130" cy="-20" r="3"/>
      <circle cx="100" cy="80" r="2.5"/><circle cx="-110" cy="60" r="2.5"/>
      <circle cx="150" cy="20" r="2"/><circle cx="-150" cy="-50" r="2"/>
    </g>
  </g>
  <!-- portrait silhouette suggestion (left side) -->
  <g opacity="0.85">
    <path d="M0 300 L0 80 Q15 40 50 30 Q90 25 105 60 Q115 100 90 130 Q120 145 110 200 Q130 240 100 280 Q70 300 60 300 Z" fill="#1A1D24"/>
  </g>
  <!-- script accent -->
  <path d="M260 70 Q300 50 340 80" stroke="#B45A3F" stroke-width="1.2" fill="none"/>
</svg>`;

/* --- 3. LC Studio Tutto --- vibrant mural / tree memory --- */
SVG.lc_underbelly = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" fill="#1A1D24"/>
  <!-- underpass arch -->
  <path d="M0 300 L0 220 Q200 30 400 220 L400 300 Z" fill="#232830"/>
  <!-- mural section under arch -->
  <path d="M40 300 L40 235 Q200 80 360 235 L360 300 Z" fill="#FBF1DC"/>
  <!-- vibrant mural elements -->
  <g>
    <!-- big bold flower -->
    <g transform="translate(150 230)">
      <ellipse cx="0" cy="-15" rx="22" ry="28" fill="#E0904A"/>
      <ellipse cx="-22" cy="0" rx="28" ry="22" fill="#B45A3F"/>
      <ellipse cx="22" cy="0" rx="28" ry="22" fill="#E2A455"/>
      <ellipse cx="0" cy="20" rx="22" ry="28" fill="#BC4D3F"/>
      <circle r="14" fill="#FBF1DC"/>
      <circle r="6" fill="#1A1D24"/>
    </g>
    <!-- bird/figure -->
    <g transform="translate(260 220)">
      <path d="M-30 0 Q-20 -25 0 -22 Q22 -28 35 -10 Q44 5 30 18 Q10 28 -10 22 Q-32 15 -30 0Z" fill="#466F95"/>
      <circle cx="20" cy="-8" r="3" fill="#FBF1DC"/>
      <path d="M30 -5 L48 -2 L42 6Z" fill="#E0C588"/>
    </g>
    <!-- swirls / abstract leaves -->
    <g fill="none" stroke="#6B7B4E" stroke-width="3">
      <path d="M70 270 Q90 240 80 215 Q105 230 110 260"/>
      <path d="M310 270 Q295 245 320 230 Q335 250 330 268"/>
    </g>
    <!-- accent dots -->
    <g fill="#E0C588">
      <circle cx="100" cy="180" r="4"/><circle cx="200" cy="160" r="3"/><circle cx="300" cy="180" r="4"/>
    </g>
  </g>
  <!-- pillar shadows -->
  <rect x="20" y="220" width="14" height="80" fill="#0E1115"/>
  <rect x="366" y="220" width="14" height="80" fill="#0E1115"/>
</svg>`;

SVG.lc_treememory = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="ltm" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#EAE3D2"/><stop offset="1" stop-color="#C8BC9B"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#ltm)"/>
  <!-- ghosted tree silhouette -->
  <g transform="translate(200 290)">
    <path d="M-12 0 L-12 -90 Q-30 -100 -25 -130 Q-50 -140 -45 -170 Q-60 -180 -55 -210 Q-30 -218 -15 -200 Q-5 -210 0 -220 Q10 -210 15 -200 Q35 -218 55 -212 Q60 -180 50 -175 Q60 -150 45 -140 Q40 -120 25 -110 Q22 -95 12 -90 L12 0 Z"
          fill="#6B7B4E" opacity="0.55"/>
    <!-- wind/seed swirls -->
    <g fill="#B68A3F" opacity="0.75">
      <circle cx="-90" cy="-160" r="3"/><circle cx="-115" cy="-130" r="2.5"/><circle cx="-140" cy="-100" r="2"/>
      <circle cx="80" cy="-180" r="3"/><circle cx="105" cy="-140" r="2.5"/><circle cx="135" cy="-110" r="2"/>
      <circle cx="-60" cy="-50" r="2"/><circle cx="60" cy="-40" r="2"/>
    </g>
    <g stroke="#B68A3F" fill="none" stroke-width="0.6" opacity="0.7">
      <path d="M-90 -160 Q-115 -140 -140 -100"/>
      <path d="M80 -180 Q105 -150 135 -110"/>
    </g>
  </g>
  <!-- foreground figure (memory) -->
  <g transform="translate(60 230)" opacity="0.85">
    <path d="M0 0 Q-2 -25 8 -38 Q5 -55 18 -55 Q30 -55 28 -38 Q38 -25 36 0 L36 70 L0 70 Z" fill="#1A1D24"/>
  </g>
</svg>`;

/* --- 4. Raphael Delgado --- california bear / cubist abstract --- */
SVG.delgado_bear = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="rd1" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#F5F1EA"/><stop offset="1" stop-color="#E0C588"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#rd1)"/>
  <!-- Cubist California bear -->
  <g transform="translate(40 60)">
    <!-- body silhouette in faceted polygons -->
    <polygon points="40,180 70,140 110,150 130,120 170,110 210,120 240,150 280,160 300,200 280,230 240,225 200,220 150,225 100,220 60,210" fill="#1A1D24"/>
    <!-- head -->
    <polygon points="240,150 260,110 290,100 305,130 295,160 270,165" fill="#1A1D24"/>
    <!-- ear -->
    <polygon points="285,108 297,90 308,108 298,118" fill="#1A1D24"/>
    <!-- internal facets -->
    <g fill="none" stroke="#E0904A" stroke-width="0.8" opacity="0.9">
      <path d="M70 140 L130 120 L170 110 L210 120 L240 150"/>
      <path d="M100 220 L130 190 L170 195 L210 188 L240 195"/>
      <path d="M260 110 L295 130 L270 165"/>
      <path d="M130 120 L150 165"/>
      <path d="M210 120 L195 175"/>
    </g>
    <!-- color block accents inside -->
    <polygon points="130,120 170,110 150,165" fill="#B45A3F" opacity="0.85"/>
    <polygon points="195,175 210,188 170,195" fill="#466F95" opacity="0.7"/>
    <polygon points="60,210 100,220 80,200" fill="#6B7B4E" opacity="0.8"/>
    <polygon points="240,150 260,110 290,100" fill="#B68A3F" opacity="0.8"/>
    <!-- eye -->
    <circle cx="278" cy="124" r="2.5" fill="#FBF1DC"/>
  </g>
  <!-- ground line -->
  <line x1="20" y1="245" x2="380" y2="245" stroke="#1A1D24" stroke-width="0.5" opacity="0.4"/>
  <!-- star -->
  <polygon points="50,40 53,48 62,48 55,54 58,62 50,57 42,62 45,54 38,48 47,48" fill="#B45A3F"/>
</svg>`;

SVG.delgado_cubist = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" fill="#FBF8F2"/>
  <!-- cubist figurative composition -->
  <g>
    <polygon points="40,40 160,30 200,90 130,140 60,120" fill="#466F95"/>
    <polygon points="160,30 280,50 250,130 200,90" fill="#E0904A"/>
    <polygon points="280,50 360,80 340,160 250,130" fill="#B68A3F"/>
    <polygon points="60,120 130,140 110,220 30,200" fill="#1A1D24"/>
    <polygon points="130,140 200,90 250,130 220,200 150,220" fill="#FBF1DC"/>
    <polygon points="250,130 340,160 320,250 230,250 220,200" fill="#B45A3F"/>
    <polygon points="30,200 110,220 90,280 20,270" fill="#6B7B4E"/>
    <polygon points="150,220 220,200 230,250 200,290 150,290" fill="#142838"/>
    <polygon points="220,200 230,250 200,290 250,300 320,250" fill="#88A8C7"/>
    <!-- linear overlay -->
    <g fill="none" stroke="#1A1D24" stroke-width="0.6" opacity="0.9">
      <path d="M40 40 L160 30 L280 50 L360 80"/>
      <path d="M160 30 L200 90 L250 130 L340 160"/>
      <path d="M40 40 L60 120 L30 200 L20 270"/>
      <path d="M130 140 L110 220 L90 280"/>
      <path d="M200 90 L130 140"/>
      <path d="M250 130 L220 200 L200 290"/>
    </g>
    <!-- abstract eye/face element -->
    <circle cx="155" cy="120" r="6" fill="#1A1D24"/>
    <circle cx="155" cy="120" r="2" fill="#FBF1DC"/>
  </g>
</svg>`;

/* --- 5. David Garibaldi --- live action paint / pop portrait --- */
SVG.garibaldi_live = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" fill="#0E1115"/>
  <!-- splatter background -->
  <g>
    <ellipse cx="120" cy="120" rx="80" ry="60" fill="#B45A3F" opacity="0.85"/>
    <ellipse cx="280" cy="170" rx="90" ry="60" fill="#E0904A" opacity="0.8"/>
    <ellipse cx="200" cy="80" rx="55" ry="40" fill="#E0C588" opacity="0.75"/>
    <ellipse cx="320" cy="80" rx="40" ry="30" fill="#B68A3F" opacity="0.9"/>
    <ellipse cx="80" cy="250" rx="60" ry="35" fill="#466F95" opacity="0.85"/>
  </g>
  <!-- gestural strokes -->
  <g fill="none" stroke-linecap="round" stroke-width="6">
    <path d="M50 80 Q120 60 200 100" stroke="#FBF1DC"/>
    <path d="M180 220 Q250 200 350 240" stroke="#FBF1DC"/>
    <path d="M30 200 Q80 180 130 210" stroke="#B45A3F"/>
    <path d="M250 60 Q300 90 360 70" stroke="#142838"/>
  </g>
  <!-- splatter dots -->
  <g fill="#FBF1DC">
    <circle cx="60" cy="50" r="3"/><circle cx="350" cy="40" r="2"/><circle cx="380" cy="120" r="2.5"/>
    <circle cx="20" cy="160" r="2"/><circle cx="370" cy="280" r="2.5"/><circle cx="40" cy="280" r="2"/>
  </g>
  <g fill="#B45A3F">
    <circle cx="200" cy="170" r="3"/><circle cx="220" cy="200" r="2"/><circle cx="160" cy="180" r="1.5"/>
  </g>
  <!-- hint of figure emerging from paint -->
  <g opacity="0.85">
    <path d="M180 100 Q200 70 230 80 Q240 100 230 130 Q260 140 250 180 Q270 220 240 240 Q200 230 180 200 Q160 170 180 100Z" fill="#1A1D24"/>
    <circle cx="210" cy="105" r="3" fill="#FBF1DC"/>
  </g>
</svg>`;

SVG.garibaldi_pop = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="dgp" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#E0904A"/><stop offset="1" stop-color="#B45A3F"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#dgp)"/>
  <!-- bold pop-portrait silhouette -->
  <g transform="translate(200 180)">
    <!-- shoulders -->
    <path d="M-110 120 Q-90 60 -50 50 L50 50 Q90 60 110 120 L110 120 L-110 120Z" fill="#1A1D24"/>
    <!-- head -->
    <ellipse cx="0" cy="-10" rx="55" ry="68" fill="#1A1D24"/>
    <!-- hair flourish -->
    <path d="M-55 -25 Q-90 -60 -70 -90 Q-30 -100 0 -78 Q30 -100 70 -90 Q90 -60 55 -25 Q60 -55 0 -50 Q-60 -55 -55 -25Z" fill="#142838"/>
    <!-- highlight -->
    <ellipse cx="-25" cy="-30" rx="14" ry="24" fill="#FBF1DC" opacity="0.85"/>
    <ellipse cx="-22" cy="-32" rx="6" ry="14" fill="#E0C588" opacity="0.9"/>
    <!-- mouth -->
    <path d="M-12 22 Q0 32 12 22" stroke="#FBF1DC" stroke-width="2" fill="none"/>
    <!-- speed/paint accents -->
    <g stroke="#FBF1DC" stroke-width="3" stroke-linecap="round" fill="none">
      <path d="M-160 -90 L-120 -70"/>
      <path d="M-150 -50 L-130 -45"/>
      <path d="M150 -90 L120 -70"/>
      <path d="M-180 60 L-150 70"/>
    </g>
  </g>
  <!-- splatter -->
  <g fill="#FBF1DC" opacity="0.9">
    <circle cx="40" cy="40" r="3"/><circle cx="360" cy="60" r="3"/>
    <circle cx="30" cy="240" r="2"/><circle cx="380" cy="260" r="2.5"/>
  </g>
</svg>`;

/* --- 6. Jaya King --- 21st Tapestry / encaustic --- */
SVG.king_tapestry = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" fill="#FBF1DC"/>
  <!-- woven tapestry pattern -->
  <g>
    ${(() => { const palette=['#B45A3F','#E0904A','#B68A3F','#6B7B4E','#466F95','#142838','#E2A455','#88A8C7'];
      let s=''; for(let r=0;r<10;r++){ for(let c=0;c<14;c++){ const x=c*30; const y=r*30; const color=palette[(r*3+c*5)%palette.length]; s+=`<rect x="${x}" y="${y}" width="30" height="30" fill="${color}"/>`;
      // diamond pattern overlay
      s+=`<polygon points="${x+15},${y+4} ${x+26},${y+15} ${x+15},${y+26} ${x+4},${y+15}" fill="${palette[(r+c+2)%palette.length]}" opacity="0.6"/>`;
      } } return s; })()}
  </g>
  <!-- texture -->
  <g stroke="#1A1D24" stroke-width="0.3" opacity="0.18">
    ${(() => { let s=''; for(let i=0;i<14;i++) s+=`<line x1="${i*30}" y1="0" x2="${i*30}" y2="300"/>`; return s; })()}
    ${(() => { let s=''; for(let i=0;i<11;i++) s+=`<line x1="0" y1="${i*30}" x2="400" y2="${i*30}"/>`; return s; })()}
  </g>
</svg>`;

SVG.king_encaustic = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="enc1" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FBF1DC"/><stop offset="1" stop-color="#E0C588"/>
    </linearGradient>
    <radialGradient id="encWax" cx="0.5" cy="0.5"><stop offset="0" stop-color="#fff" stop-opacity="0.6"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
  </defs>
  <rect width="400" height="300" fill="url(#enc1)"/>
  <!-- soft wax layers, panel grid -->
  <g>
    <rect x="20" y="20" width="115" height="115" fill="#B45A3F" opacity="0.78"/>
    <rect x="20" y="20" width="115" height="115" fill="url(#encWax)"/>
    <rect x="142" y="20" width="115" height="115" fill="#466F95" opacity="0.72"/>
    <rect x="142" y="20" width="115" height="115" fill="url(#encWax)"/>
    <rect x="265" y="20" width="115" height="115" fill="#B68A3F" opacity="0.85"/>
    <rect x="265" y="20" width="115" height="115" fill="url(#encWax)"/>
    <rect x="20" y="142" width="115" height="138" fill="#142838" opacity="0.85"/>
    <rect x="20" y="142" width="115" height="138" fill="url(#encWax)"/>
    <rect x="142" y="142" width="115" height="138" fill="#E0904A" opacity="0.8"/>
    <rect x="142" y="142" width="115" height="138" fill="url(#encWax)"/>
    <rect x="265" y="142" width="115" height="138" fill="#6B7B4E" opacity="0.78"/>
    <rect x="265" y="142" width="115" height="138" fill="url(#encWax)"/>
  </g>
  <!-- gold leaf flecks -->
  <g fill="#E0C588" opacity="0.75">
    <rect x="40" y="60" width="30" height="3"/>
    <rect x="170" y="100" width="22" height="3"/>
    <rect x="290" y="80" width="28" height="3"/>
    <rect x="60" y="200" width="22" height="3"/>
    <rect x="180" y="240" width="28" height="3"/>
    <rect x="300" y="180" width="22" height="3"/>
  </g>
  <!-- drips -->
  <g stroke="#1A1D24" stroke-width="0.6" fill="none" opacity="0.4">
    <path d="M70 50 Q72 80 70 110"/>
    <path d="M210 60 Q213 95 210 120"/>
    <path d="M320 200 Q318 230 322 250"/>
  </g>
</svg>`;

/* --- 7. Grigio Art Consulting --- curated wall / healthcare --- */
SVG.grigio_curated = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" fill="#EAE3D2"/>
  <!-- gallery wall: salon-hung mixed frames -->
  <g>
    <!-- big landscape -->
    <rect x="30" y="40" width="160" height="100" fill="#fff" stroke="#1A1D24"/>
    <rect x="38" y="48" width="144" height="84" fill="#88A8C7"/>
    <path d="M38 110 Q70 90 100 100 Q140 88 182 110 L182 132 L38 132 Z" fill="#466F95"/>
    <circle cx="160" cy="60" r="6" fill="#E0C588"/>
    <!-- portrait -->
    <rect x="210" y="20" width="80" height="120" fill="#fff" stroke="#1A1D24"/>
    <rect x="218" y="28" width="64" height="104" fill="#B45A3F"/>
    <ellipse cx="250" cy="60" rx="14" ry="18" fill="#1A1D24"/>
    <path d="M230 100 Q250 88 270 100 L270 130 L230 130Z" fill="#1A1D24"/>
    <!-- small abstract -->
    <rect x="310" y="40" width="60" height="60" fill="#fff" stroke="#1A1D24"/>
    <rect x="316" y="46" width="48" height="48" fill="#FBF1DC"/>
    <circle cx="332" cy="62" r="8" fill="#E0904A"/>
    <rect x="340" y="74" width="20" height="14" fill="#142838"/>
    <!-- horizontal -->
    <rect x="50" y="160" width="180" height="50" fill="#fff" stroke="#1A1D24"/>
    <rect x="58" y="168" width="164" height="34" fill="#1A1D24"/>
    <g stroke="#E0C588" stroke-width="1" fill="none">
      <path d="M58 180 L222 180"/><path d="M58 192 L222 192"/>
    </g>
    <!-- ovals -->
    <ellipse cx="290" cy="180" rx="35" ry="24" fill="#fff" stroke="#1A1D24"/>
    <ellipse cx="290" cy="180" rx="29" ry="18" fill="#6B7B4E"/>
    <!-- small -->
    <rect x="350" y="160" width="34" height="40" fill="#fff" stroke="#1A1D24"/>
    <rect x="354" y="164" width="26" height="32" fill="#B68A3F"/>
    <!-- bench / floor line -->
    <line x1="0" y1="245" x2="400" y2="245" stroke="#1A1D24" stroke-width="1"/>
    <rect x="80" y="245" width="240" height="6" fill="#1A1D24"/>
    <rect x="100" y="251" width="200" height="20" fill="#1A1D24" opacity="0.4"/>
  </g>
</svg>`;

SVG.grigio_healthcare = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="ghc" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FBF8F2"/><stop offset="1" stop-color="#D6E2EE"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#ghc)"/>
  <!-- abstracted clinic interior -->
  <!-- floor -->
  <polygon points="0,300 400,300 400,200 0,200" fill="#EAE3D2"/>
  <!-- back wall with art -->
  <rect x="40" y="60" width="320" height="140" fill="#FBF8F2"/>
  <!-- triptych -->
  <rect x="80" y="90" width="60" height="80" fill="#88A8C7"/>
  <rect x="150" y="90" width="60" height="80" fill="#466F95"/>
  <rect x="220" y="90" width="60" height="80" fill="#142838"/>
  <!-- horizon line -->
  <line x1="80" y1="130" x2="280" y2="130" stroke="#E0C588" stroke-width="1"/>
  <!-- plant sculpture -->
  <g transform="translate(310 110)">
    <rect x="-12" y="40" width="24" height="60" fill="#1A1D24"/>
    <ellipse cx="0" cy="20" rx="22" ry="32" fill="#6B7B4E"/>
    <ellipse cx="0" cy="0" rx="14" ry="20" fill="#88A8C7" opacity="0.7"/>
  </g>
  <!-- bench -->
  <rect x="100" y="220" width="200" height="14" fill="#B68A3F"/>
  <rect x="105" y="234" width="6" height="40" fill="#1A1D24"/>
  <rect x="289" y="234" width="6" height="40" fill="#1A1D24"/>
  <!-- person silhouette -->
  <g transform="translate(170 200)" opacity="0.55">
    <circle cx="0" cy="-8" r="6" fill="#1A1D24"/>
    <path d="M-8 0 L-10 22 L-4 22 L-4 8 L4 8 L4 22 L10 22 L8 0Z" fill="#1A1D24"/>
  </g>
</svg>`;

/* --- 8. Jose Di Gregorio --- kaleidoscope / celestial --- */
SVG.digregorio_kaleido = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" fill="#142838"/>
  <g transform="translate(200 150)">
    ${(() => {
      const cols = ['#E0904A','#B45A3F','#E0C588','#88A8C7','#466F95','#6B7B4E','#FBF1DC','#B68A3F'];
      let s = '';
      for (let i = 0; i < 12; i++) {
        const a = i * 30;
        s += `<g transform="rotate(${a})">`;
        s += `<polygon points="0,0 50,-12 80,0 50,12" fill="${cols[i%cols.length]}"/>`;
        s += `<polygon points="80,0 110,-8 140,0 110,8" fill="${cols[(i+3)%cols.length]}"/>`;
        s += `<circle cx="65" cy="0" r="5" fill="${cols[(i+1)%cols.length]}"/>`;
        s += `<polygon points="30,-20 40,-30 50,-20 40,-10" fill="${cols[(i+5)%cols.length]}"/>`;
        s += `</g>`;
      }
      return s;
    })()}
    <circle r="14" fill="#FBF1DC"/>
    <circle r="6" fill="#B68A3F"/>
  </g>
  <!-- corner facets -->
  <g fill="none" stroke="#88A8C7" stroke-width="0.5" opacity="0.5">
    <circle cx="200" cy="150" r="80"/>
    <circle cx="200" cy="150" r="120"/>
  </g>
</svg>`;

SVG.digregorio_celestial = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="cel" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0E1B30"/><stop offset="0.5" stop-color="#1B3050"/><stop offset="1" stop-color="#142838"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#cel)"/>
  <!-- distant mountain silhouette -->
  <polygon points="0,220 60,180 110,200 170,160 230,190 290,170 360,200 400,180 400,300 0,300" fill="#0A0F1C"/>
  <!-- moon -->
  <circle cx="300" cy="80" r="30" fill="#FBF1DC"/>
  <circle cx="293" cy="74" r="28" fill="#142838"/>
  <!-- stars -->
  <g fill="#FBF1DC">
    ${(() => { let s=''; for(let i=0;i<60;i++){ const x=Math.random()*400, y=Math.random()*180, r=Math.random()*1.4+0.3; s+=`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${r.toFixed(1)}"/>`; } return s; })()}
  </g>
  <!-- sacred geometry overlay -->
  <g fill="none" stroke="#E0C588" stroke-width="0.6" opacity="0.85">
    <circle cx="200" cy="150" r="56"/>
    <circle cx="172" cy="150" r="56"/>
    <circle cx="228" cy="150" r="56"/>
    <circle cx="200" cy="122" r="56"/>
    <circle cx="200" cy="178" r="56"/>
    <polygon points="200,90 256,178 144,178" fill="none" stroke="#E0C588"/>
  </g>
  <!-- shooting star -->
  <line x1="40" y1="40" x2="120" y2="80" stroke="#E0C588" stroke-width="1"/>
  <circle cx="125" cy="82" r="2" fill="#FBF1DC"/>
</svg>`;

/* --- 9. Micah Crandall-Bear --- color field horizon --- */
SVG.crandall_field = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="cb1" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FBE5C9"/>
      <stop offset="0.32" stop-color="#E2A455"/>
      <stop offset="0.5" stop-color="#B45A3F"/>
      <stop offset="0.55" stop-color="#5A4055"/>
      <stop offset="0.7" stop-color="#1B3050"/>
      <stop offset="1" stop-color="#0A0F1C"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#cb1)"/>
  <!-- soft horizon banding (Rothko-like) -->
  <g opacity="0.8">
    <rect x="0" y="50" width="400" height="2" fill="#FBE5C9" opacity="0.4"/>
    <rect x="0" y="120" width="400" height="2" fill="#FBE5C9" opacity="0.55"/>
    <rect x="0" y="146" width="400" height="3" fill="#1A1D24" opacity="0.5"/>
    <rect x="0" y="180" width="400" height="2" fill="#88A8C7" opacity="0.3"/>
  </g>
  <!-- subtle texture -->
  <g fill="#FBF1DC" opacity="0.06">
    ${(() => { let s=''; for (let i=0;i<200;i++){ const x=Math.random()*400, y=Math.random()*300, r=Math.random()*1.2; s+=`<circle cx="${x.toFixed(0)}" cy="${y.toFixed(0)}" r="${r.toFixed(1)}"/>`; } return s; })()}
  </g>
</svg>`;

SVG.crandall_horizon = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="cb2" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#D6E2EE"/>
      <stop offset="0.3" stop-color="#88A8C7"/>
      <stop offset="0.5" stop-color="#466F95"/>
      <stop offset="0.55" stop-color="#FBF1DC"/>
      <stop offset="0.62" stop-color="#E0904A"/>
      <stop offset="1" stop-color="#1A1D24"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#cb2)"/>
  <g opacity="0.75">
    <rect x="0" y="150" width="400" height="2" fill="#FBF1DC"/>
    <rect x="0" y="158" width="400" height="1" fill="#FBF1DC" opacity="0.5"/>
    <rect x="0" y="200" width="400" height="2" fill="#1A1D24" opacity="0.5"/>
  </g>
  <g fill="#1A1D24" opacity="0.04">
    ${(() => { let s=''; for (let i=0;i<200;i++){ const x=Math.random()*400, y=Math.random()*300, r=Math.random()*1.2; s+=`<circle cx="${x.toFixed(0)}" cy="${y.toFixed(0)}" r="${r.toFixed(1)}"/>`; } return s; })()}
  </g>
</svg>`;

/* --- 10. Gale Hart --- Missing the Mark / pop sculpt --- */
SVG.hart_missingmark = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" fill="#FBF1DC"/>
  <!-- dartboard -->
  <g transform="translate(200 150)">
    <circle r="120" fill="#1A1D24"/>
    <circle r="105" fill="#FBF1DC"/>
    <circle r="100" fill="#1A1D24"/>
    <circle r="80" fill="#B45A3F"/>
    <circle r="60" fill="#FBF1DC"/>
    <circle r="40" fill="#1A1D24"/>
    <circle r="22" fill="#B45A3F"/>
    <circle r="8" fill="#1A1D24"/>
    <!-- segment dividers (12-spoke) -->
    <g stroke="#FBF1DC" stroke-width="1" opacity="0.85">
      ${(() => { let s=''; for(let i=0;i<20;i++){ const a=i*18*Math.PI/180; s+=`<line x1="${(40*Math.cos(a)).toFixed(1)}" y1="${(40*Math.sin(a)).toFixed(1)}" x2="${(100*Math.cos(a)).toFixed(1)}" y2="${(100*Math.sin(a)).toFixed(1)}"/>`; } return s; })()}
    </g>
  </g>
  <!-- darts way off mark -->
  <g>
    <g transform="translate(60 60) rotate(35)">
      <line x1="0" y1="0" x2="40" y2="0" stroke="#1A1D24" stroke-width="2"/>
      <polygon points="40,0 36,-3 36,3" fill="#1A1D24"/>
      <polygon points="0,0 -8,-4 -8,4" fill="#B45A3F"/>
    </g>
    <g transform="translate(340 250) rotate(-50)">
      <line x1="0" y1="0" x2="40" y2="0" stroke="#1A1D24" stroke-width="2"/>
      <polygon points="40,0 36,-3 36,3" fill="#1A1D24"/>
      <polygon points="0,0 -8,-4 -8,4" fill="#466F95"/>
    </g>
    <g transform="translate(330 70) rotate(160)">
      <line x1="0" y1="0" x2="40" y2="0" stroke="#1A1D24" stroke-width="2"/>
      <polygon points="40,0 36,-3 36,3" fill="#1A1D24"/>
      <polygon points="0,0 -8,-4 -8,4" fill="#E0904A"/>
    </g>
  </g>
</svg>`;

SVG.hart_popsculpt = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="hps" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#D6E2EE"/><stop offset="1" stop-color="#88A8C7"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#hps)"/>
  <!-- gallery floor -->
  <polygon points="0,260 400,260 400,300 0,300" fill="#1A1D24"/>
  <!-- pedestal -->
  <rect x="155" y="200" width="90" height="60" fill="#FBF1DC"/>
  <rect x="155" y="200" width="90" height="6" fill="#E0C588"/>
  <!-- pop sculpture -->
  <g transform="translate(200 180)">
    <!-- abstract heart/balloon form -->
    <path d="M-50 0 Q-50 -50 0 -55 Q50 -50 50 0 Q50 30 0 60 Q-50 30 -50 0Z" fill="#B45A3F"/>
    <ellipse cx="-20" cy="-20" rx="15" ry="20" fill="#FBF1DC" opacity="0.7"/>
    <!-- bolt of lightning across -->
    <polygon points="-15,-10 5,-15 -5,15 15,10 -2,40 8,15 -8,18 0,-12" fill="#E0C588"/>
  </g>
  <!-- shadow -->
  <ellipse cx="200" cy="262" rx="50" ry="6" fill="#1A1D24" opacity="0.4"/>
</svg>`;

/* --- 11. Stephanie Taylor --- dance tribute / historic --- */
SVG.taylor_dance = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="td1" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FBE5C9"/><stop offset="1" stop-color="#E0904A"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#td1)"/>
  <!-- silhouette dancers -->
  <g fill="#1A1D24">
    <g transform="translate(80 160)">
      <circle cx="0" cy="-50" r="8"/>
      <path d="M-12 -45 Q-25 -30 -10 -10 L-5 0 L-15 30 L-10 32 L0 5 L10 32 L15 30 L5 0 L10 -10 Q25 -30 12 -45Z"/>
    </g>
    <g transform="translate(180 150) rotate(-8)">
      <circle cx="0" cy="-55" r="9"/>
      <path d="M-15 -50 Q-30 -25 -5 -8 L-3 5 L-22 35 L-15 38 L0 12 L15 38 L22 35 L3 5 L5 -8 Q30 -25 15 -50Z"/>
      <!-- raised arm -->
      <path d="M10 -40 Q35 -55 45 -75 L42 -78 Q30 -60 8 -42Z"/>
    </g>
    <g transform="translate(280 165) rotate(10)">
      <circle cx="0" cy="-50" r="8"/>
      <path d="M-12 -45 Q-25 -28 -8 -10 L-2 5 L-18 32 L-12 35 L2 8 L18 35 L24 32 L8 5 L14 -10 Q30 -28 14 -45Z"/>
    </g>
  </g>
  <!-- arc of motion -->
  <path d="M40 90 Q200 30 360 90" stroke="#B45A3F" stroke-width="2" fill="none" opacity="0.85"/>
  <!-- musical staff hint -->
  <g stroke="#1A1D24" stroke-width="0.4" opacity="0.6">
    <line x1="0" y1="240" x2="400" y2="240"/>
    <line x1="0" y1="248" x2="400" y2="248"/>
    <line x1="0" y1="256" x2="400" y2="256"/>
  </g>
  <circle cx="120" cy="250" r="4" fill="#1A1D24"/>
  <line x1="124" y1="250" x2="124" y2="232" stroke="#1A1D24" stroke-width="1"/>
  <circle cx="280" cy="244" r="4" fill="#1A1D24"/>
  <line x1="284" y1="244" x2="284" y2="226" stroke="#1A1D24" stroke-width="1"/>
</svg>`;

SVG.taylor_historic = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="th1" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#E2C994"/><stop offset="1" stop-color="#B68A3F"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#th1)"/>
  <!-- river / sky -->
  <rect x="0" y="170" width="400" height="80" fill="#466F95"/>
  <!-- bridge silhouette (Tower Bridge style) -->
  <g fill="#1A1D24">
    <rect x="100" y="120" width="40" height="80"/>
    <rect x="260" y="120" width="40" height="80"/>
    <polygon points="100,120 120,90 140,120"/>
    <polygon points="260,120 280,90 300,120"/>
    <rect x="115" y="100" width="10" height="20"/>
    <rect x="275" y="100" width="10" height="20"/>
    <rect x="140" y="160" width="120" height="14"/>
    <!-- cables -->
    <g stroke="#1A1D24" stroke-width="1" fill="none">
      <path d="M120 90 L140 160"/><path d="M120 90 L160 160"/><path d="M120 90 L180 160"/>
      <path d="M280 90 L260 160"/><path d="M280 90 L240 160"/><path d="M280 90 L220 160"/>
    </g>
  </g>
  <!-- river reflection -->
  <g opacity="0.5">
    <rect x="100" y="174" width="40" height="40" fill="#1A1D24"/>
    <rect x="260" y="174" width="40" height="40" fill="#1A1D24"/>
    <rect x="140" y="174" width="120" height="6" fill="#1A1D24"/>
  </g>
  <!-- ripples -->
  <g stroke="#FBF1DC" stroke-width="0.6" fill="none" opacity="0.6">
    <path d="M40 220 Q60 217 80 220 Q100 223 120 220"/>
    <path d="M280 230 Q300 227 320 230 Q340 233 360 230"/>
    <path d="M140 240 Q160 237 180 240 Q200 243 220 240"/>
  </g>
  <!-- vintage figures -->
  <g fill="#1A1D24">
    <circle cx="50" cy="245" r="3"/>
    <rect x="48" y="248" width="4" height="14"/>
    <circle cx="380" cy="252" r="3"/>
    <rect x="378" y="255" width="4" height="14"/>
  </g>
</svg>`;

/* --- 12. Franceska Gamez --- phoenix / floral portrait --- */
SVG.gamez_phoenix = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="ph1" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1A1D24"/><stop offset="1" stop-color="#0E1115"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#ph1)"/>
  <!-- phoenix body -->
  <g transform="translate(200 170)">
    <!-- tail flames -->
    <g>
      <path d="M-20 30 Q-50 60 -90 80 Q-60 60 -45 30 Q-30 50 -20 30Z" fill="#B45A3F"/>
      <path d="M0 45 Q-20 90 -45 110 Q-25 80 -10 45Z" fill="#E0904A"/>
      <path d="M20 30 Q50 60 90 80 Q60 60 45 30 Q30 50 20 30Z" fill="#B45A3F"/>
      <path d="M0 45 Q20 90 45 110 Q25 80 10 45Z" fill="#E0904A"/>
    </g>
    <!-- body -->
    <ellipse cx="0" cy="0" rx="22" ry="32" fill="#FBF1DC"/>
    <!-- wings spread -->
    <path d="M-22 -10 Q-90 -40 -120 -20 Q-100 -30 -80 -45 Q-50 -55 -22 -25Z" fill="#E2A455"/>
    <path d="M22 -10 Q90 -40 120 -20 Q100 -30 80 -45 Q50 -55 22 -25Z" fill="#E2A455"/>
    <path d="M-15 -25 Q-60 -50 -100 -55 Q-70 -68 -40 -65 Q-20 -55 -15 -25Z" fill="#B45A3F"/>
    <path d="M15 -25 Q60 -50 100 -55 Q70 -68 40 -65 Q20 -55 15 -25Z" fill="#B45A3F"/>
    <!-- head -->
    <ellipse cx="0" cy="-32" rx="13" ry="18" fill="#FBF1DC"/>
    <polygon points="0,-44 -3,-50 3,-50" fill="#E0904A"/>
    <polygon points="-2,-30 -10,-26 -2,-22" fill="#E0904A"/>
    <polygon points="2,-30 10,-26 2,-22" fill="#E0904A"/>
    <!-- eye -->
    <circle cx="0" cy="-34" r="2" fill="#1A1D24"/>
    <!-- crest -->
    <path d="M-3 -45 Q-8 -55 -2 -52 L-1 -48Z" fill="#B45A3F"/>
    <path d="M3 -45 Q8 -55 2 -52 L1 -48Z" fill="#B45A3F"/>
  </g>
  <!-- ember sparks -->
  <g fill="#E0C588">
    <circle cx="60" cy="60" r="2"/><circle cx="340" cy="80" r="2"/><circle cx="80" cy="220" r="1.5"/>
    <circle cx="320" cy="240" r="2"/><circle cx="40" cy="160" r="1.5"/><circle cx="370" cy="140" r="1.5"/>
  </g>
</svg>`;

SVG.gamez_floral = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" fill="#FBE5C9"/>
  <!-- portrait silhouette -->
  <g transform="translate(220 180)">
    <ellipse cx="0" cy="-30" rx="50" ry="60" fill="#B68A3F"/>
    <path d="M-50 30 Q-30 10 0 8 Q30 10 50 30 L60 130 L-60 130Z" fill="#1A1D24"/>
    <ellipse cx="0" cy="-30" rx="50" ry="60" fill="#1A1D24" opacity="0.45"/>
  </g>
  <!-- giant floral hair/headdress -->
  <g transform="translate(200 110)">
    <g>
      <ellipse cx="-60" cy="-10" rx="35" ry="40" fill="#B45A3F"/>
      <ellipse cx="-30" cy="-50" rx="40" ry="35" fill="#E0904A"/>
      <ellipse cx="20" cy="-50" rx="40" ry="35" fill="#E2A455"/>
      <ellipse cx="60" cy="-10" rx="35" ry="40" fill="#B45A3F"/>
      <ellipse cx="0" cy="-30" rx="50" ry="40" fill="#FBF1DC"/>
    </g>
    <!-- centers -->
    <g fill="#1A1D24">
      <circle cx="-60" cy="-10" r="8"/><circle cx="-30" cy="-50" r="8"/>
      <circle cx="20" cy="-50" r="8"/><circle cx="60" cy="-10" r="8"/>
      <circle cx="0" cy="-30" r="8"/>
    </g>
    <!-- leaves -->
    <g fill="#6B7B4E">
      <ellipse cx="-90" cy="20" rx="14" ry="6" transform="rotate(-30 -90 20)"/>
      <ellipse cx="90" cy="20" rx="14" ry="6" transform="rotate(30 90 20)"/>
      <ellipse cx="-100" cy="-20" rx="14" ry="6" transform="rotate(-60 -100 -20)"/>
      <ellipse cx="100" cy="-20" rx="14" ry="6" transform="rotate(60 100 -20)"/>
    </g>
  </g>
</svg>`;

/* --- 13. Shaun Burner --- jazz portrait / symbolist --- */
SVG.burner_jazz = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bj1" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0A0F1C"/><stop offset="1" stop-color="#1B3050"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#bj1)"/>
  <!-- spotlight -->
  <radialGradient id="spot" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#E0C588" stop-opacity="0.4"/>
    <stop offset="1" stop-color="#E0C588" stop-opacity="0"/>
  </radialGradient>
  <ellipse cx="200" cy="120" rx="180" ry="100" fill="url(#spot)"/>
  <!-- portrait -->
  <g transform="translate(200 180)">
    <!-- shoulders -->
    <path d="M-90 100 Q-80 60 -50 50 L50 50 Q80 60 90 100 L90 120 L-90 120Z" fill="#142838"/>
    <!-- neck -->
    <rect x="-15" y="30" width="30" height="30" fill="#7A5A3D"/>
    <!-- face -->
    <ellipse cx="0" cy="-10" rx="42" ry="55" fill="#9D7A5A"/>
    <!-- hair -->
    <path d="M-40 -50 Q-50 -80 -10 -85 Q30 -85 40 -50 Q35 -65 0 -68 Q-30 -65 -40 -50Z" fill="#1A1D24"/>
    <!-- eyes -->
    <ellipse cx="-15" cy="-15" rx="4" ry="3" fill="#1A1D24"/>
    <ellipse cx="15" cy="-15" rx="4" ry="3" fill="#1A1D24"/>
    <!-- lipstick -->
    <path d="M-12 18 Q0 24 12 18 Q5 26 0 25 Q-5 26 -12 18Z" fill="#B45A3F"/>
    <!-- earring -->
    <circle cx="-38" cy="0" r="3" fill="#E0C588"/>
    <circle cx="38" cy="0" r="3" fill="#E0C588"/>
  </g>
  <!-- musical notes / saxophone curve -->
  <g stroke="#E0C588" stroke-width="1.5" fill="none" opacity="0.8">
    <path d="M40 80 Q60 90 60 110 Q60 130 40 130 Q20 130 20 115"/>
  </g>
  <g fill="#E0C588">
    <circle cx="350" cy="60" r="3"/><line x1="353" y1="60" x2="353" y2="40" stroke="#E0C588" stroke-width="1"/>
    <circle cx="370" cy="100" r="3"/><line x1="373" y1="100" x2="373" y2="80" stroke="#E0C588" stroke-width="1"/>
    <circle cx="60" cy="200" r="2.5"/>
  </g>
</svg>`;

SVG.burner_symbolist = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="sym1" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#3D2C4D"/><stop offset="1" stop-color="#0E1115"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#sym1)"/>
  <!-- moon/eye -->
  <circle cx="200" cy="100" r="50" fill="#FBF1DC"/>
  <circle cx="200" cy="100" r="30" fill="#142838"/>
  <circle cx="200" cy="100" r="14" fill="#1A1D24"/>
  <circle cx="195" cy="95" r="3" fill="#FBF1DC"/>
  <!-- hand reaching -->
  <g transform="translate(200 250) rotate(-5)" fill="#9D7A5A">
    <ellipse cx="0" cy="0" rx="22" ry="14"/>
    <rect x="-5" y="-30" width="6" height="32" rx="3"/>
    <rect x="3" y="-34" width="6" height="36" rx="3"/>
    <rect x="-12" y="-26" width="6" height="28" rx="3"/>
    <rect x="-19" y="-20" width="6" height="22" rx="3"/>
    <rect x="11" y="-14" width="14" height="8" rx="3"/>
    <rect x="-30" y="0" width="60" height="20"/>
  </g>
  <!-- floating symbols -->
  <g fill="#E0C588" opacity="0.85">
    <polygon points="80,80 84,90 94,90 86,96 89,106 80,100 71,106 74,96 66,90 76,90"/>
    <polygon points="320,80 324,90 334,90 326,96 329,106 320,100 311,106 314,96 306,90 316,90"/>
    <circle cx="60" cy="180" r="6"/>
    <circle cx="340" cy="180" r="6"/>
    <path d="M40 230 Q50 220 60 230 Q50 240 40 230Z"/>
    <path d="M340 230 Q350 220 360 230 Q350 240 340 230Z"/>
  </g>
  <!-- thread connecting -->
  <g stroke="#E0C588" stroke-width="0.5" fill="none" opacity="0.6">
    <path d="M150 100 Q120 200 200 250"/>
    <path d="M250 100 Q280 200 200 250"/>
  </g>
</svg>`;

/* --- 14. Jeremiah Kille --- elephant / balloons --- */
SVG.kille_elephant = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="ke1" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#E2C994"/><stop offset="1" stop-color="#B68A3F"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#ke1)"/>
  <!-- ground -->
  <ellipse cx="200" cy="280" rx="200" ry="20" fill="#6B7B4E" opacity="0.5"/>
  <!-- elephant body -->
  <g transform="translate(180 180)">
    <!-- body -->
    <ellipse cx="0" cy="0" rx="100" ry="55" fill="#7A6B7E"/>
    <!-- head -->
    <ellipse cx="-95" cy="-20" rx="50" ry="48" fill="#7A6B7E"/>
    <!-- ears -->
    <ellipse cx="-105" cy="-30" rx="32" ry="40" fill="#5C4F61"/>
    <ellipse cx="-115" cy="-22" rx="20" ry="28" fill="#7A6B7E"/>
    <!-- trunk -->
    <path d="M-130 0 Q-160 30 -150 60 Q-140 80 -115 70 Q-100 50 -110 30 Q-125 10 -130 0Z" fill="#7A6B7E"/>
    <!-- legs -->
    <rect x="-60" y="40" width="22" height="60" fill="#7A6B7E"/>
    <rect x="-20" y="40" width="22" height="60" fill="#7A6B7E"/>
    <rect x="40" y="40" width="22" height="60" fill="#7A6B7E"/>
    <rect x="80" y="40" width="22" height="60" fill="#7A6B7E"/>
    <!-- tail -->
    <path d="M100 -10 Q120 0 122 30" stroke="#7A6B7E" stroke-width="3" fill="none"/>
    <circle cx="122" cy="32" r="3" fill="#1A1D24"/>
    <!-- eye -->
    <circle cx="-105" cy="-25" r="3" fill="#1A1D24"/>
    <!-- tusk -->
    <path d="M-128 5 Q-135 20 -128 28 L-122 25 Q-122 14 -128 5Z" fill="#FBF1DC"/>
    <!-- texture wash painting feel -->
    <path d="M-50 -35 Q0 -45 60 -32 Q90 -30 95 -10" stroke="#5C4F61" stroke-width="1" fill="none" opacity="0.8"/>
  </g>
  <!-- bird companion -->
  <g transform="translate(120 110)">
    <ellipse cx="0" cy="0" rx="14" ry="8" fill="#E0904A"/>
    <circle cx="10" cy="-2" r="5" fill="#E0904A"/>
    <polygon points="14,-2 22,-1 16,3" fill="#1A1D24"/>
    <circle cx="11" cy="-3" r="1.2" fill="#1A1D24"/>
  </g>
</svg>`;

SVG.kille_balloons = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="kb1" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FBE5C9"/><stop offset="0.5" stop-color="#E2A455"/><stop offset="1" stop-color="#B45A3F"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#kb1)"/>
  <!-- distant land -->
  <polygon points="0,250 400,250 400,300 0,300" fill="#3D2C4D"/>
  <polygon points="0,240 80,210 140,235 220,205 290,230 360,205 400,240 400,250 0,250" fill="#5C4F61"/>
  <!-- balloon 1 -->
  <g transform="translate(120 130)">
    <ellipse cx="0" cy="0" rx="38" ry="48" fill="#B45A3F"/>
    <path d="M-15 -30 Q0 -35 15 -30 Q15 -10 -15 -10Z" fill="#FBF1DC" opacity="0.5"/>
    <rect x="-12" y="48" width="24" height="14" fill="#7A5A3D"/>
    <!-- tethers -->
    <line x1="-12" y1="48" x2="-15" y2="35" stroke="#1A1D24" stroke-width="0.5"/>
    <line x1="12" y1="48" x2="15" y2="35" stroke="#1A1D24" stroke-width="0.5"/>
    <line x1="0" y1="48" x2="0" y2="35" stroke="#1A1D24" stroke-width="0.5"/>
  </g>
  <!-- balloon 2 -->
  <g transform="translate(280 90)">
    <ellipse cx="0" cy="0" rx="32" ry="40" fill="#E0904A"/>
    <path d="M-10 -25 Q0 -28 10 -25 Q10 -8 -10 -8Z" fill="#FBF1DC" opacity="0.5"/>
    <rect x="-10" y="40" width="20" height="12" fill="#7A5A3D"/>
    <line x1="-10" y1="40" x2="-12" y2="28" stroke="#1A1D24" stroke-width="0.5"/>
    <line x1="10" y1="40" x2="12" y2="28" stroke="#1A1D24" stroke-width="0.5"/>
  </g>
  <!-- balloon 3 -->
  <g transform="translate(330 200)">
    <ellipse cx="0" cy="0" rx="22" ry="28" fill="#142838"/>
    <rect x="-7" y="28" width="14" height="9" fill="#7A5A3D"/>
  </g>
  <!-- birds -->
  <g stroke="#1A1D24" stroke-width="1" fill="none">
    <path d="M40 60 Q50 55 60 60 Q70 55 80 60"/>
    <path d="M180 40 Q190 35 200 40 Q210 35 220 40"/>
  </g>
  <!-- sun -->
  <circle cx="60" cy="80" r="18" fill="#FBF1DC" opacity="0.85"/>
</svg>`;

/* --- 15. Anthony Padilla (Kinetik) --- character / abstract --- */
SVG.padilla_character = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="ap1" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#B45A3F"/><stop offset="0.5" stop-color="#E0904A"/><stop offset="1" stop-color="#142838"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#ap1)"/>
  <!-- aerosol character -->
  <g transform="translate(200 160)">
    <!-- abstract head -->
    <path d="M-80 -50 Q-90 -90 -40 -100 Q0 -110 50 -95 Q90 -85 80 -40 Q90 0 70 30 Q40 60 0 55 Q-50 50 -80 20 Q-100 0 -80 -50Z" fill="#FBF1DC"/>
    <!-- big eye -->
    <circle cx="-15" cy="-30" r="22" fill="#FBF1DC"/>
    <circle cx="-15" cy="-30" r="20" fill="#142838"/>
    <circle cx="-15" cy="-30" r="14" fill="#88A8C7"/>
    <circle cx="-15" cy="-30" r="6" fill="#1A1D24"/>
    <circle cx="-12" cy="-32" r="2" fill="#FBF1DC"/>
    <!-- second eye / abstract -->
    <ellipse cx="38" cy="-20" rx="14" ry="10" fill="#1A1D24"/>
    <circle cx="38" cy="-20" r="4" fill="#FBF1DC"/>
    <!-- mouth -->
    <path d="M-30 25 Q0 45 35 25 L35 35 Q0 55 -30 35Z" fill="#1A1D24"/>
    <line x1="-15" y1="32" x2="-15" y2="48" stroke="#FBF1DC" stroke-width="1"/>
    <line x1="0" y1="35" x2="0" y2="51" stroke="#FBF1DC" stroke-width="1"/>
    <line x1="15" y1="32" x2="15" y2="48" stroke="#FBF1DC" stroke-width="1"/>
    <!-- spray accents -->
    <g fill="#E0904A">
      <circle cx="-100" cy="-80" r="3"/><circle cx="-115" cy="-60" r="2"/>
      <circle cx="100" cy="-80" r="3"/><circle cx="115" cy="-60" r="2"/>
    </g>
  </g>
  <!-- drips -->
  <g stroke="#FBF1DC" stroke-width="2" fill="none" opacity="0.85">
    <path d="M120 230 Q123 260 120 290"/>
    <path d="M280 230 Q283 260 280 290"/>
  </g>
</svg>`;

SVG.padilla_color = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="ap2" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#B45A3F"/><stop offset="0.3" stop-color="#E0904A"/><stop offset="0.7" stop-color="#E2A455"/><stop offset="1" stop-color="#FBF1DC"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#ap2)"/>
  <!-- spray strokes -->
  <g fill="none" stroke-linecap="round" stroke-width="20" opacity="0.85">
    <path d="M0 80 Q150 60 400 90" stroke="#1A1D24"/>
    <path d="M0 140 Q200 130 400 160" stroke="#FBF1DC" opacity="0.6"/>
    <path d="M0 200 Q150 180 400 210" stroke="#142838" opacity="0.7"/>
  </g>
  <!-- drip patches -->
  <g>
    <ellipse cx="80" cy="80" rx="40" ry="14" fill="#142838" opacity="0.6"/>
    <ellipse cx="320" cy="200" rx="40" ry="14" fill="#FBF1DC" opacity="0.5"/>
  </g>
  <!-- spray dot scatter -->
  <g fill="#1A1D24" opacity="0.7">
    ${(() => { let s=''; for(let i=0;i<50;i++){ s+=`<circle cx="${(Math.random()*400).toFixed(0)}" cy="${(Math.random()*300).toFixed(0)}" r="${(Math.random()*1.4+0.4).toFixed(1)}"/>`; } return s; })()}
  </g>
  <g fill="#FBF1DC" opacity="0.75">
    ${(() => { let s=''; for(let i=0;i<40;i++){ s+=`<circle cx="${(Math.random()*400).toFixed(0)}" cy="${(Math.random()*300).toFixed(0)}" r="${(Math.random()*1.2+0.3).toFixed(1)}"/>`; } return s; })()}
  </g>
</svg>`;

/* --- 16. John S. Huerta --- Frida / Día de los Muertos --- */
SVG.huerta_frida = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="fr1" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#6B7B4E"/><stop offset="1" stop-color="#1A1D24"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#fr1)"/>
  <!-- frida portrait -->
  <g transform="translate(200 180)">
    <!-- shoulders -->
    <path d="M-90 110 Q-80 60 -50 50 L50 50 Q80 60 90 110 L90 130 L-90 130Z" fill="#B45A3F"/>
    <!-- neck -->
    <rect x="-15" y="30" width="30" height="32" fill="#9D7A5A"/>
    <!-- face -->
    <ellipse cx="0" cy="-10" rx="46" ry="58" fill="#9D7A5A"/>
    <!-- iconic unibrow -->
    <path d="M-30 -30 Q-15 -36 0 -30 Q15 -36 30 -30" stroke="#1A1D24" stroke-width="3" fill="none"/>
    <!-- eyes -->
    <ellipse cx="-15" cy="-20" rx="5" ry="3" fill="#1A1D24"/>
    <ellipse cx="15" cy="-20" rx="5" ry="3" fill="#1A1D24"/>
    <!-- nose hint -->
    <path d="M-3 -5 Q0 5 3 -5" stroke="#1A1D24" stroke-width="0.6" fill="none"/>
    <!-- lips -->
    <path d="M-12 12 Q0 22 12 12 Q5 18 0 18 Q-5 18 -12 12Z" fill="#B45A3F"/>
    <line x1="-12" y1="12" x2="12" y2="12" stroke="#1A1D24" stroke-width="0.5"/>
    <!-- hair -->
    <path d="M-46 -50 Q-50 -90 0 -90 Q50 -90 46 -50 Q40 -68 0 -65 Q-40 -68 -46 -50Z" fill="#1A1D24"/>
    <!-- earring -->
    <circle cx="-42" cy="0" r="3" fill="#E0C588"/>
    <circle cx="42" cy="0" r="3" fill="#E0C588"/>
  </g>
  <!-- floral crown -->
  <g transform="translate(200 100)">
    <circle cx="-30" cy="-15" r="14" fill="#B45A3F"/>
    <circle cx="0" cy="-25" r="16" fill="#E0904A"/>
    <circle cx="30" cy="-15" r="14" fill="#FBF1DC"/>
    <circle cx="-50" cy="-5" r="10" fill="#E2A455"/>
    <circle cx="50" cy="-5" r="10" fill="#B45A3F"/>
    <g fill="#1A1D24">
      <circle cx="-30" cy="-15" r="4"/><circle cx="0" cy="-25" r="4"/>
      <circle cx="30" cy="-15" r="4"/><circle cx="-50" cy="-5" r="3"/><circle cx="50" cy="-5" r="3"/>
    </g>
    <!-- leaves -->
    <ellipse cx="-65" cy="0" rx="10" ry="4" fill="#6B7B4E" transform="rotate(-30 -65 0)"/>
    <ellipse cx="65" cy="0" rx="10" ry="4" fill="#6B7B4E" transform="rotate(30 65 0)"/>
  </g>
</svg>`;

SVG.huerta_diamuertos = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="dm1" cx="0.5" cy="0.4" r="0.7">
      <stop offset="0" stop-color="#B45A3F"/><stop offset="1" stop-color="#1A1D24"/>
    </radialGradient>
  </defs>
  <rect width="400" height="300" fill="url(#dm1)"/>
  <!-- sugar skull -->
  <g transform="translate(200 150)">
    <!-- skull -->
    <path d="M-60 -50 Q-80 -10 -70 30 L-50 70 Q-30 80 0 80 Q30 80 50 70 L70 30 Q80 -10 60 -50 Q40 -80 0 -80 Q-40 -80 -60 -50Z" fill="#FBF1DC"/>
    <!-- eye sockets - flowers -->
    <g transform="translate(-25 -20)">
      <circle r="14" fill="#1A1D24"/>
      <g fill="#B45A3F">
        <circle cx="-8" cy="0" r="4"/><circle cx="8" cy="0" r="4"/>
        <circle cx="0" cy="-8" r="4"/><circle cx="0" cy="8" r="4"/>
      </g>
      <circle r="4" fill="#E0C588"/>
    </g>
    <g transform="translate(25 -20)">
      <circle r="14" fill="#1A1D24"/>
      <g fill="#E0904A">
        <circle cx="-8" cy="0" r="4"/><circle cx="8" cy="0" r="4"/>
        <circle cx="0" cy="-8" r="4"/><circle cx="0" cy="8" r="4"/>
      </g>
      <circle r="4" fill="#FBF1DC"/>
    </g>
    <!-- nose triangle -->
    <polygon points="0,-5 -7,15 7,15" fill="#1A1D24"/>
    <!-- teeth grin -->
    <rect x="-25" y="35" width="50" height="14" fill="#FBF1DC" stroke="#1A1D24"/>
    <g stroke="#1A1D24" stroke-width="1">
      <line x1="-15" y1="35" x2="-15" y2="49"/>
      <line x1="-5" y1="35" x2="-5" y2="49"/>
      <line x1="5" y1="35" x2="5" y2="49"/>
      <line x1="15" y1="35" x2="15" y2="49"/>
    </g>
    <!-- decoration -->
    <g fill="#466F95">
      <circle cx="-40" cy="50" r="3"/><circle cx="40" cy="50" r="3"/>
      <circle cx="-50" cy="20" r="3"/><circle cx="50" cy="20" r="3"/>
      <circle cx="0" cy="-65" r="4"/><circle cx="-25" cy="-60" r="3"/><circle cx="25" cy="-60" r="3"/>
    </g>
    <!-- forehead heart -->
    <path d="M-8 -55 Q-16 -65 0 -65 Q16 -65 8 -55 Q16 -45 0 -40 Q-16 -45 -8 -55Z" fill="#B45A3F"/>
    <!-- swirls -->
    <g stroke="#B45A3F" stroke-width="1" fill="none">
      <path d="M-55 -30 Q-65 -25 -60 -10"/>
      <path d="M55 -30 Q65 -25 60 -10"/>
    </g>
  </g>
  <!-- marigolds floating -->
  <g fill="#E0904A">
    <circle cx="40" cy="60" r="12"/><circle cx="40" cy="60" r="6" fill="#B45A3F"/>
    <circle cx="360" cy="80" r="10"/><circle cx="360" cy="80" r="5" fill="#B45A3F"/>
    <circle cx="60" cy="240" r="8"/><circle cx="60" cy="240" r="4" fill="#B45A3F"/>
    <circle cx="350" cy="240" r="10"/><circle cx="350" cy="240" r="5" fill="#B45A3F"/>
  </g>
</svg>`;

/* --- 17. Waylon Horner --- cartoonish / surreal --- */
SVG.horner_cartoon = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="wh1" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#88A8C7"/><stop offset="1" stop-color="#FBE5C9"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#wh1)"/>
  <!-- whimsical character -->
  <g transform="translate(200 170)">
    <!-- body -->
    <ellipse cx="0" cy="20" rx="60" ry="50" fill="#E0904A" stroke="#1A1D24" stroke-width="3"/>
    <!-- head -->
    <circle cx="0" cy="-30" r="48" fill="#FBF1DC" stroke="#1A1D24" stroke-width="3"/>
    <!-- big cartoon eyes -->
    <circle cx="-18" cy="-35" r="14" fill="#FBF1DC" stroke="#1A1D24" stroke-width="2"/>
    <circle cx="18" cy="-35" r="14" fill="#FBF1DC" stroke="#1A1D24" stroke-width="2"/>
    <circle cx="-18" cy="-32" r="6" fill="#1A1D24"/>
    <circle cx="18" cy="-32" r="6" fill="#1A1D24"/>
    <circle cx="-16" cy="-34" r="2" fill="#FBF1DC"/>
    <circle cx="20" cy="-34" r="2" fill="#FBF1DC"/>
    <!-- cheeks -->
    <ellipse cx="-30" cy="-15" rx="6" ry="4" fill="#B45A3F" opacity="0.6"/>
    <ellipse cx="30" cy="-15" rx="6" ry="4" fill="#B45A3F" opacity="0.6"/>
    <!-- big toothy smile -->
    <path d="M-22 -10 Q0 10 22 -10 Q0 -2 -22 -10Z" fill="#1A1D24"/>
    <rect x="-15" y="-10" width="6" height="6" fill="#FBF1DC"/>
    <rect x="-7" y="-10" width="6" height="6" fill="#FBF1DC"/>
    <rect x="1" y="-10" width="6" height="6" fill="#FBF1DC"/>
    <rect x="9" y="-10" width="6" height="6" fill="#FBF1DC"/>
    <!-- ears/horns -->
    <polygon points="-32,-65 -38,-85 -22,-72" fill="#FBF1DC" stroke="#1A1D24" stroke-width="2"/>
    <polygon points="32,-65 38,-85 22,-72" fill="#FBF1DC" stroke="#1A1D24" stroke-width="2"/>
    <!-- arms -->
    <path d="M-55 0 Q-90 10 -85 40" stroke="#1A1D24" stroke-width="3" fill="none"/>
    <path d="M55 0 Q90 10 85 40" stroke="#1A1D24" stroke-width="3" fill="none"/>
    <circle cx="-85" cy="42" r="8" fill="#FBF1DC" stroke="#1A1D24" stroke-width="2"/>
    <circle cx="85" cy="42" r="8" fill="#FBF1DC" stroke="#1A1D24" stroke-width="2"/>
  </g>
  <!-- speech sparkle -->
  <g fill="#FBF1DC" stroke="#1A1D24" stroke-width="1.5">
    <polygon points="60,60 65,72 78,72 68,80 72,93 60,85 48,93 52,80 42,72 55,72"/>
    <polygon points="340,80 345,90 358,90 348,98 352,110 340,103 328,110 332,98 322,90 335,90"/>
  </g>
</svg>`;

SVG.horner_surreal = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="ws1" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#3D2C4D"/><stop offset="1" stop-color="#0E1115"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#ws1)"/>
  <!-- floating eye -->
  <g transform="translate(120 100)">
    <ellipse cx="0" cy="0" rx="50" ry="35" fill="#FBF1DC" stroke="#1A1D24" stroke-width="2"/>
    <circle cx="0" cy="0" r="22" fill="#88A8C7"/>
    <circle cx="0" cy="0" r="12" fill="#1A1D24"/>
    <circle cx="3" cy="-3" r="3" fill="#FBF1DC"/>
    <!-- lashes -->
    <g stroke="#1A1D24" stroke-width="1.5">
      <line x1="-30" y1="-25" x2="-35" y2="-32"/>
      <line x1="-15" y1="-32" x2="-17" y2="-40"/>
      <line x1="0" y1="-35" x2="0" y2="-44"/>
      <line x1="15" y1="-32" x2="17" y2="-40"/>
      <line x1="30" y1="-25" x2="35" y2="-32"/>
    </g>
  </g>
  <!-- melted clock -->
  <g transform="translate(280 160) rotate(15)">
    <ellipse cx="0" cy="0" rx="36" ry="38" fill="#E0904A" stroke="#1A1D24" stroke-width="2"/>
    <path d="M-36 0 Q-34 60 -10 90 Q10 80 14 50 L36 -10Z" fill="#E0904A" stroke="#1A1D24" stroke-width="2"/>
    <line x1="0" y1="0" x2="0" y2="-22" stroke="#1A1D24" stroke-width="2"/>
    <line x1="0" y1="0" x2="20" y2="0" stroke="#1A1D24" stroke-width="2"/>
    <circle cx="0" cy="0" r="3" fill="#1A1D24"/>
    <g fill="#1A1D24">
      <circle cx="0" cy="-28" r="1.5"/><circle cx="28" cy="0" r="1.5"/>
      <circle cx="0" cy="28" r="1.5"/><circle cx="-28" cy="0" r="1.5"/>
    </g>
  </g>
  <!-- spiral -->
  <g transform="translate(200 230)" fill="none" stroke="#E0C588" stroke-width="1.2">
    <path d="M0 0 Q 8 -8 16 0 Q 8 8 -8 0 Q -16 -16 8 -24 Q 32 -8 24 16"/>
  </g>
  <!-- floating teeth -->
  <g fill="#FBF1DC" stroke="#1A1D24" stroke-width="1">
    <path d="M50 240 L60 240 L58 256 L52 256Z"/>
    <path d="M340 80 L350 80 L348 96 L342 96Z"/>
    <path d="M70 160 L80 160 L78 176 L72 176Z"/>
  </g>
  <!-- stars -->
  <g fill="#E0C588">
    <circle cx="220" cy="60" r="2"/><circle cx="50" cy="50" r="1.5"/>
    <circle cx="370" cy="50" r="2"/><circle cx="370" cy="220" r="1.5"/>
  </g>
</svg>`;

/* --- 18. Skinner --- creature (lighter side) / pop bright --- */
SVG.skinner_creature = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="sk1" cx="0.5" cy="0.5" r="0.7">
      <stop offset="0" stop-color="#E0C588"/><stop offset="1" stop-color="#B45A3F"/>
    </radialGradient>
  </defs>
  <rect width="400" height="300" fill="url(#sk1)"/>
  <!-- friendly creature -->
  <g transform="translate(200 170)">
    <!-- body -->
    <ellipse cx="0" cy="20" rx="80" ry="60" fill="#88A8C7" stroke="#1A1D24" stroke-width="3"/>
    <!-- white belly -->
    <ellipse cx="0" cy="35" rx="50" ry="35" fill="#FBF1DC"/>
    <!-- big head -->
    <circle cx="0" cy="-40" r="55" fill="#88A8C7" stroke="#1A1D24" stroke-width="3"/>
    <!-- eyes (multiple — friendly weird) -->
    <circle cx="-22" cy="-50" r="14" fill="#FBF1DC" stroke="#1A1D24" stroke-width="2"/>
    <circle cx="22" cy="-50" r="14" fill="#FBF1DC" stroke="#1A1D24" stroke-width="2"/>
    <circle cx="0" cy="-72" r="10" fill="#FBF1DC" stroke="#1A1D24" stroke-width="2"/>
    <circle cx="-22" cy="-50" r="6" fill="#1A1D24"/>
    <circle cx="22" cy="-50" r="6" fill="#1A1D24"/>
    <circle cx="0" cy="-72" r="4" fill="#1A1D24"/>
    <!-- horns/spikes -->
    <polygon points="-40,-78 -50,-100 -28,-90" fill="#E0904A" stroke="#1A1D24" stroke-width="2"/>
    <polygon points="40,-78 50,-100 28,-90" fill="#E0904A" stroke="#1A1D24" stroke-width="2"/>
    <!-- mouth (smiling, friendly) -->
    <path d="M-30 -25 Q0 -5 30 -25" stroke="#1A1D24" stroke-width="3" fill="none"/>
    <!-- tongue / fang -->
    <path d="M-10 -20 Q0 -8 10 -20 L8 -12 Q0 -4 -8 -12Z" fill="#B45A3F"/>
    <!-- legs -->
    <ellipse cx="-50" cy="80" rx="14" ry="10" fill="#88A8C7" stroke="#1A1D24" stroke-width="2"/>
    <ellipse cx="50" cy="80" rx="14" ry="10" fill="#88A8C7" stroke="#1A1D24" stroke-width="2"/>
    <!-- belly spots -->
    <circle cx="-15" cy="40" r="4" fill="#E0904A"/>
    <circle cx="15" cy="50" r="4" fill="#E0904A"/>
    <circle cx="0" cy="20" r="3" fill="#E0904A"/>
  </g>
  <!-- rainbow accent -->
  <g fill="none" stroke-width="3">
    <path d="M30 80 Q60 60 90 80" stroke="#B45A3F"/>
    <path d="M30 84 Q60 64 90 84" stroke="#E0904A"/>
    <path d="M30 88 Q60 68 90 88" stroke="#E0C588"/>
    <path d="M30 92 Q60 72 90 92" stroke="#6B7B4E"/>
    <path d="M30 96 Q60 76 90 96" stroke="#466F95"/>
  </g>
</svg>`;

SVG.skinner_pop = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" fill="#FBF1DC"/>
  <!-- pop psychedelic radiating -->
  <g transform="translate(200 150)">
    ${(() => {
      const cols = ['#B45A3F','#E0904A','#E0C588','#6B7B4E','#466F95','#88A8C7','#142838','#E2A455'];
      let s = '';
      for (let i = 0; i < 18; i++) {
        const a1 = i * 20;
        const a2 = a1 + 20;
        const x1 = Math.cos(a1*Math.PI/180)*200;
        const y1 = Math.sin(a1*Math.PI/180)*200;
        const x2 = Math.cos(a2*Math.PI/180)*200;
        const y2 = Math.sin(a2*Math.PI/180)*200;
        s += `<polygon points="0,0 ${x1.toFixed(0)},${y1.toFixed(0)} ${x2.toFixed(0)},${y2.toFixed(0)}" fill="${cols[i%cols.length]}" opacity="0.85"/>`;
      }
      return s;
    })()}
    <!-- center smiley -->
    <circle r="40" fill="#FBF1DC" stroke="#1A1D24" stroke-width="3"/>
    <circle cx="-12" cy="-8" r="4" fill="#1A1D24"/>
    <circle cx="12" cy="-8" r="4" fill="#1A1D24"/>
    <path d="M-15 8 Q0 22 15 8" stroke="#1A1D24" stroke-width="2.5" fill="none"/>
  </g>
</svg>`;

/* --- 19. Groundswell Art --- gallery / clean --- */
SVG.groundswell_gallery = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" fill="#FBF8F2"/>
  <!-- gallery interior -->
  <!-- floor with perspective -->
  <polygon points="0,300 400,300 320,200 80,200" fill="#E2C994"/>
  <polygon points="80,200 320,200 280,180 120,180" fill="#D6C8A4"/>
  <!-- walls -->
  <polygon points="0,0 80,200 0,300" fill="#F0EBE0"/>
  <polygon points="400,0 320,200 400,300" fill="#F0EBE0"/>
  <rect x="80" y="0" width="240" height="200" fill="#FFFFFF"/>
  <line x1="80" y1="200" x2="320" y2="200" stroke="#D6C8A4" stroke-width="1"/>
  <!-- art on back wall -->
  <rect x="120" y="40" width="50" height="70" fill="#1A1D24"/>
  <rect x="180" y="50" width="60" height="50" fill="#88A8C7"/>
  <rect x="250" y="40" width="40" height="80" fill="#B45A3F"/>
  <!-- spotlights -->
  <g fill="#E0C588" opacity="0.4">
    <polygon points="145,0 130,40 170,40"/>
    <polygon points="210,0 200,50 240,50"/>
    <polygon points="270,0 250,40 290,40"/>
  </g>
  <!-- bench -->
  <rect x="160" y="220" width="80" height="6" fill="#1A1D24"/>
  <rect x="165" y="226" width="4" height="20" fill="#1A1D24"/>
  <rect x="231" y="226" width="4" height="20" fill="#1A1D24"/>
  <!-- visitor silhouette -->
  <g transform="translate(150 195)" opacity="0.8">
    <circle cx="0" cy="0" r="6" fill="#1A1D24"/>
    <path d="M-7 5 L-9 25 L-3 25 L-3 14 L3 14 L3 25 L9 25 L7 5Z" fill="#1A1D24"/>
  </g>
</svg>`;

SVG.groundswell_clean = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" fill="#F4F1EA"/>
  <!-- minimal sculpture installation -->
  <line x1="0" y1="240" x2="400" y2="240" stroke="#1A1D24" stroke-width="0.5" opacity="0.4"/>
  <!-- forms -->
  <g>
    <!-- monolith -->
    <rect x="80" y="80" width="40" height="160" fill="#1A1D24"/>
    <rect x="80" y="80" width="40" height="14" fill="#E0C588"/>
    <!-- sphere -->
    <circle cx="200" cy="200" r="38" fill="#466F95"/>
    <ellipse cx="186" cy="185" rx="14" ry="8" fill="#88A8C7" opacity="0.6"/>
    <!-- pyramid/wedge -->
    <polygon points="280,240 320,140 360,240" fill="#B45A3F"/>
    <polygon points="280,240 320,140 320,240" fill="#1A1D24" opacity="0.3"/>
    <!-- shadows -->
    <ellipse cx="100" cy="244" rx="22" ry="3" fill="#1A1D24" opacity="0.3"/>
    <ellipse cx="200" cy="244" rx="36" ry="4" fill="#1A1D24" opacity="0.3"/>
    <ellipse cx="320" cy="244" rx="38" ry="3" fill="#1A1D24" opacity="0.3"/>
  </g>
  <!-- gentle ground texture -->
  <g fill="#1A1D24" opacity="0.05">
    ${(() => { let s=''; for(let i=0;i<60;i++){ s+=`<circle cx="${(Math.random()*400).toFixed(0)}" cy="${(240+Math.random()*60).toFixed(0)}" r="${(Math.random()*1.2+0.3).toFixed(1)}"/>`; } return s; })()}
  </g>
</svg>`;

/* --- 20. Wide Open Walls --- mural city / festival --- */
SVG.wow_muralcity = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="wow1" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FBE5C9"/><stop offset="1" stop-color="#E0904A"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#wow1)"/>
  <!-- street -->
  <rect x="0" y="240" width="400" height="60" fill="#1A1D24"/>
  <line x1="0" y1="270" x2="400" y2="270" stroke="#FBF1DC" stroke-width="1" stroke-dasharray="14 14"/>
  <!-- buildings with murals -->
  <!-- building 1 -->
  <rect x="20" y="80" width="100" height="160" fill="#FBF1DC"/>
  <!-- mural 1 -->
  <g>
    <rect x="20" y="80" width="100" height="160" fill="#B45A3F" opacity="0.85"/>
    <ellipse cx="70" cy="140" rx="30" ry="40" fill="#FBF1DC"/>
    <circle cx="70" cy="125" r="14" fill="#1A1D24"/>
    <path d="M50 200 Q70 180 90 200 L90 230 L50 230Z" fill="#1A1D24"/>
    <path d="M30 90 Q60 95 90 90 Q120 95 110 110" stroke="#E0C588" stroke-width="2" fill="none"/>
  </g>
  <!-- building 2 (taller) -->
  <rect x="135" y="40" width="120" height="200" fill="#88A8C7"/>
  <!-- mural 2 - geometric -->
  <g>
    <polygon points="135,40 195,40 200,140 135,160" fill="#142838"/>
    <polygon points="195,40 255,40 255,140 200,140" fill="#E0904A"/>
    <polygon points="135,160 200,140 255,140 255,240 135,240" fill="#FBF1DC"/>
    <circle cx="195" cy="190" r="30" fill="#B45A3F"/>
    <circle cx="195" cy="190" r="14" fill="#142838"/>
  </g>
  <!-- building 3 -->
  <rect x="270" y="100" width="110" height="140" fill="#FBF1DC"/>
  <g>
    <!-- bird mural -->
    <path d="M280 130 Q300 100 340 110 Q370 125 365 160 Q350 185 320 180 Q290 175 280 150Z" fill="#6B7B4E"/>
    <ellipse cx="310" cy="140" rx="6" ry="4" fill="#FBF1DC"/>
    <polygon points="365,150 380,148 370,160" fill="#E0904A"/>
    <path d="M280 200 Q320 195 360 200 L360 230 L280 230Z" fill="#1A1D24"/>
  </g>
  <!-- streetlamp -->
  <g fill="#1A1D24">
    <rect x="125" y="160" width="2" height="80"/>
    <ellipse cx="126" cy="158" rx="6" ry="4"/>
  </g>
</svg>`;

SVG.wow_festival = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="wf1" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#88A8C7"/><stop offset="1" stop-color="#FBE5C9"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#wf1)"/>
  <!-- aerial city block -->
  <g>
    <!-- streets -->
    <rect x="0" y="120" width="400" height="20" fill="#1A1D24" opacity="0.55"/>
    <rect x="0" y="220" width="400" height="20" fill="#1A1D24" opacity="0.55"/>
    <rect x="120" y="0" width="20" height="300" fill="#1A1D24" opacity="0.55"/>
    <rect x="260" y="0" width="20" height="300" fill="#1A1D24" opacity="0.55"/>
    <!-- block 1 (top-left) -->
    <rect x="0" y="0" width="120" height="120" fill="#B45A3F"/>
    <circle cx="60" cy="60" r="30" fill="#FBF1DC"/>
    <circle cx="60" cy="60" r="14" fill="#142838"/>
    <!-- block 2 -->
    <rect x="140" y="0" width="120" height="120" fill="#E0C588"/>
    <polygon points="160,20 240,20 240,100 160,100" fill="none" stroke="#1A1D24" stroke-width="2"/>
    <line x1="160" y1="20" x2="240" y2="100" stroke="#1A1D24" stroke-width="2"/>
    <!-- block 3 -->
    <rect x="280" y="0" width="120" height="120" fill="#466F95"/>
    <g fill="#FBF1DC">
      <circle cx="300" cy="40" r="6"/><circle cx="340" cy="60" r="8"/><circle cx="380" cy="40" r="6"/>
      <circle cx="320" cy="80" r="6"/><circle cx="360" cy="100" r="6"/>
    </g>
    <!-- block 4 -->
    <rect x="0" y="140" width="120" height="80" fill="#6B7B4E"/>
    <rect x="20" y="160" width="80" height="40" fill="#FBF1DC"/>
    <!-- block 5 -->
    <rect x="140" y="140" width="120" height="80" fill="#E0904A"/>
    <ellipse cx="200" cy="180" rx="40" ry="24" fill="#1A1D24"/>
    <!-- block 6 -->
    <rect x="280" y="140" width="120" height="80" fill="#FBF1DC"/>
    <g stroke="#B45A3F" stroke-width="2" fill="none">
      <path d="M295 160 Q320 150 345 160 Q370 170 385 160"/>
      <path d="M295 180 Q320 170 345 180 Q370 190 385 180"/>
      <path d="M295 200 Q320 190 345 200 Q370 210 385 200"/>
    </g>
    <!-- block 7 -->
    <rect x="0" y="240" width="120" height="60" fill="#142838"/>
    <g fill="#E0C588">
      <circle cx="40" cy="270" r="3"/><circle cx="80" cy="270" r="3"/>
      <line x1="20" y1="270" x2="100" y2="270" stroke="#E0C588" stroke-width="0.5"/>
    </g>
    <!-- block 8 -->
    <rect x="140" y="240" width="120" height="60" fill="#88A8C7"/>
    <polygon points="200,250 220,290 180,290" fill="#FBF1DC"/>
    <!-- block 9 -->
    <rect x="280" y="240" width="120" height="60" fill="#B45A3F"/>
    <g stroke="#FBF1DC" stroke-width="3" stroke-linecap="round">
      <line x1="300" y1="260" x2="320" y2="280"/>
      <line x1="340" y1="260" x2="360" y2="280"/>
      <line x1="380" y1="260" x2="395" y2="275"/>
    </g>
  </g>
</svg>`;

/* --- 21. NINE dot ARTS --- 9 dots / placemaking --- */
SVG.ninedot_logo = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" fill="#FBF8F2"/>
  <!-- 9 dots in 3x3, with one as accent -->
  <g>
    ${(() => {
      let s = '';
      const colors = ['#1A1D24','#1A1D24','#1A1D24','#1A1D24','#B68A3F','#1A1D24','#1A1D24','#1A1D24','#1A1D24'];
      for (let i = 0; i < 9; i++) {
        const r = Math.floor(i / 3);
        const c = i % 3;
        const cx = 130 + c * 70;
        const cy = 80 + r * 70;
        s += `<circle cx="${cx}" cy="${cy}" r="22" fill="${colors[i]}"/>`;
      }
      return s;
    })()}
    <!-- thin line connecting -->
    <g stroke="#B68A3F" stroke-width="0.6" fill="none" opacity="0.6">
      <path d="M130 80 L200 80 L270 80 L270 150 L130 150 L130 220 L270 220"/>
    </g>
    <!-- subtle accent circle around accent dot -->
    <circle cx="200" cy="150" r="36" fill="none" stroke="#B68A3F" stroke-width="0.8"/>
  </g>
  <!-- label-like marks -->
  <g fill="#8B8E96" opacity="0.6">
    <rect x="38" y="40" width="60" height="2"/>
    <rect x="38" y="48" width="40" height="2"/>
    <rect x="302" y="252" width="60" height="2"/>
    <rect x="322" y="260" width="40" height="2"/>
  </g>
</svg>`;

SVG.ninedot_placemaking = `
<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="ndp" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#D6E2EE"/><stop offset="1" stop-color="#88A8C7"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#ndp)"/>
  <!-- modern lobby placemaking interior -->
  <!-- floor -->
  <polygon points="0,300 400,300 400,200 0,200" fill="#E2C994"/>
  <!-- back wall -->
  <rect x="40" y="40" width="320" height="160" fill="#FBF8F2"/>
  <!-- big sculptural piece -->
  <g transform="translate(200 130)">
    <circle r="50" fill="#B45A3F"/>
    <circle r="34" fill="#FBF1DC"/>
    <circle r="20" fill="#142838"/>
    <circle r="8" fill="#E0C588"/>
    <!-- radiating elements -->
    <g stroke="#1A1D24" stroke-width="0.6" fill="none">
      <line x1="-80" y1="0" x2="-50" y2="0"/><line x1="80" y1="0" x2="50" y2="0"/>
      <line x1="0" y1="-80" x2="0" y2="-50"/><line x1="0" y1="80" x2="0" y2="50"/>
    </g>
  </g>
  <!-- side panels -->
  <rect x="60" y="60" width="14" height="120" fill="#466F95"/>
  <rect x="326" y="60" width="14" height="120" fill="#466F95"/>
  <!-- floor numbers / dots -->
  <g fill="#1A1D24">
    <circle cx="100" cy="250" r="4"/><circle cx="200" cy="270" r="4"/><circle cx="300" cy="250" r="4"/>
  </g>
  <!-- soft ceiling line -->
  <line x1="40" y1="200" x2="360" y2="200" stroke="#D6C8A4" stroke-width="1"/>
</svg>`;

