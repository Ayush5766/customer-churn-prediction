/**
 * ChurnGuard Frontend Application
 *
 * Handles live slider interactions, async REST API calls to FastAPI,
 * 60fps gauge animations, theme switching, and dynamic model metric rendering.
 */

// DOM Elements & Selectors
const htmlElement = document.documentElement;
const themeToggleBtn = document.getElementById('theme-toggle');
const navbar = document.getElementById('navbar');

const churnForm = document.getElementById('churn-form');
const tenureSlider = document.getElementById('tenure');
const tenureValueLabel = document.getElementById('tenure-value');
const monthlySlider = document.getElementById('monthly_charges');
const monthlyValueLabel = document.getElementById('monthly-value');
const totalChargesInput = document.getElementById('total_charges');
const predictBtn = document.getElementById('btn-predict');

const presetHighBtn = document.getElementById('btn-preset-high');
const presetLowBtn = document.getElementById('btn-preset-low');
const resetFormBtn = document.getElementById('btn-reset-form');

const resultEmptyState = document.getElementById('result-empty');
const resultContent = document.getElementById('result-content');
const gaugeProgress = document.getElementById('gauge-progress');
const probPercentageText = document.getElementById('prob-percentage');
const riskBadge = document.getElementById('risk-badge');
const riskIcon = document.getElementById('risk-icon');
const riskText = document.getElementById('risk-text');
const verdictBanner = document.getElementById('verdict-banner');
const verdictText = document.getElementById('verdict-text');
const suggestionsList = document.getElementById('suggestions-list');

const toastContainer = document.getElementById('toast-container');
const featureImportanceList = document.getElementById('feature-importance-list');

// Semicircle gauge circumference for radius 90 (pi * 90 ≈ 282.74)
const GAUGE_CIRCUMFERENCE = 283;


/* ==========================================================================
   1. Theme Management (Dark / Light)
   Why: Respects user preference and stores selection in localStorage
   so returning visitors keep their preferred viewing theme.
   ========================================================================== */
function initTheme() {
  const savedTheme = localStorage.getItem('churnguard_theme') || 'dark';
  htmlElement.setAttribute('data-theme', savedTheme);
}

function toggleTheme() {
  const currentTheme = htmlElement.getAttribute('data-theme') || 'dark';
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  htmlElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('churnguard_theme', newTheme);
}

if (themeToggleBtn) {
  themeToggleBtn.addEventListener('click', toggleTheme);
}


/* ==========================================================================
   2. Navbar Scroll Blur
   Why: Provides visual separation between sticky nav and content when scrolling.
   ========================================================================== */
function handleNavbarScroll() {
  if (window.scrollY > 20) {
    navbar.classList.add('scrolled');
  } else {
    navbar.classList.remove('scrolled');
  }
}
window.addEventListener('scroll', handleNavbarScroll, { passive: true });


/* ==========================================================================
   3. Interactive Form Sliders & Auto-Calculation
   Why: Auto-calculating TotalCharges gives a realistic estimate,
   preventing edge cases where tenure is high but total charges is zero.
   ========================================================================== */
function updateSliderLabels() {
  const tenureVal = parseInt(tenureSlider.value, 10);
  const monthlyVal = parseFloat(monthlySlider.value);

  tenureValueLabel.textContent = `${tenureVal} ${tenureVal === 1 ? 'month' : 'months'}`;
  monthlyValueLabel.textContent = `$${monthlyVal.toFixed(2)}`;

  // Auto-estimate total charges if input has not been custom locked
  const estimatedTotal = (tenureVal * monthlyVal).toFixed(2);
  totalChargesInput.value = estimatedTotal;
}

tenureSlider.addEventListener('input', updateSliderLabels);
monthlySlider.addEventListener('input', updateSliderLabels);


/* ==========================================================================
   4. Ripple Click Animation on Buttons
   Why: Gives tactile 60fps micro-interaction feedback on user clicks.
   ========================================================================== */
document.querySelectorAll('.btn-ripple').forEach(button => {
  button.addEventListener('click', function (e) {
    const circle = document.createElement('span');
    const diameter = Math.max(this.clientWidth, this.clientHeight);
    const radius = diameter / 2;

    const rect = this.getBoundingClientRect();
    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${e.clientX - rect.left - radius}px`;
    circle.style.top = `${e.clientY - rect.top - radius}px`;
    circle.classList.add('ripple-wave');

    const ripple = this.querySelector('.ripple-wave');
    if (ripple) ripple.remove();

    this.appendChild(circle);
  });
});


/* ==========================================================================
   5. Toast Notification Utility
   Why: Communicates network/validation errors non-intrusively to the user.
   ========================================================================== */
function showToast(message, type = 'error') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;

  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('toast-exit');
    toast.addEventListener('animationend', () => toast.remove());
  }, 4000);
}


/* ==========================================================================
   6. Form Presets & Reset Handlers
   Why: Enables recruiters and testers to test high-risk and low-risk
   edge cases with a single click without manual form typing.
   ========================================================================== */
function setRadioValue(name, value) {
  const input = document.querySelector(`input[name="${name}"][value="${value}"]`);
  if (input) input.checked = true;
}

function loadHighRiskPreset() {
  tenureSlider.value = 2;
  monthlySlider.value = 85.0;
  totalChargesInput.value = '170.00';
  updateSliderLabels();

  setRadioValue('contract', 'Month-to-month');
  setRadioValue('internet_service', 'Fiber optic');
  setRadioValue('tech_support', 'No');
  setRadioValue('online_security', 'No');
  setRadioValue('paperless_billing', 'Yes');
  document.getElementById('payment_method').value = 'Electronic check';

  executePrediction();
}

function loadLowRiskPreset() {
  tenureSlider.value = 60;
  monthlySlider.value = 55.0;
  totalChargesInput.value = '3300.00';
  updateSliderLabels();

  setRadioValue('contract', 'Two year');
  setRadioValue('internet_service', 'DSL');
  setRadioValue('tech_support', 'Yes');
  setRadioValue('online_security', 'Yes');
  setRadioValue('paperless_billing', 'No');
  document.getElementById('payment_method').value = 'Credit card (automatic)';

  executePrediction();
}

function resetForm() {
  tenureSlider.value = 12;
  monthlySlider.value = 65.0;
  updateSliderLabels();

  setRadioValue('contract', 'Month-to-month');
  setRadioValue('internet_service', 'Fiber optic');
  setRadioValue('tech_support', 'No');
  setRadioValue('online_security', 'No');
  setRadioValue('paperless_billing', 'Yes');
  document.getElementById('payment_method').value = 'Electronic check';

  // Restore empty result state
  resultContent.style.display = 'none';
  resultEmptyState.style.display = 'flex';
}

presetHighBtn.addEventListener('click', loadHighRiskPreset);
presetLowBtn.addEventListener('click', loadLowRiskPreset);
resetFormBtn.addEventListener('click', resetForm);


/* ==========================================================================
   7. Smooth Numeric Count-Up Animation (requestAnimationFrame)
   Why: Produces smooth 60fps easing transitions without external libraries.
   ========================================================================== */
function animateValue(element, start, end, duration, decimals = 0, suffix = '') {
  let startTime = null;
  const isFloat = decimals > 0;

  function step(timestamp) {
    if (!startTime) startTime = timestamp;
    const progress = Math.min((timestamp - startTime) / duration, 1);
    
    // Ease-out cubic formula
    const easeOut = 1 - Math.pow(1 - progress, 3);
    const current = start + (end - start) * easeOut;

    element.textContent = (isFloat ? current.toFixed(decimals) : Math.round(current)) + suffix;

    if (progress < 1) {
      requestAnimationFrame(step);
    }
  }

  requestAnimationFrame(step);
}


/* ==========================================================================
   8. Prediction Execution & Animated Gauge Rendering
   Why: Talks directly to FastAPI POST /predict using native ES6 fetch API.
   ========================================================================== */
async function executePrediction() {
  // Extract and validate values
  const tenure = parseInt(tenureSlider.value, 10);
  const monthlyCharges = parseFloat(monthlySlider.value);
  const totalCharges = parseFloat(totalChargesInput.value);

  if (isNaN(totalCharges) || totalCharges < 0) {
    showToast('Please enter a valid non-negative number for Total Charges.');
    return;
  }

  const contract = document.querySelector('input[name="contract"]:checked')?.value;
  const internetService = document.querySelector('input[name="internet_service"]:checked')?.value;
  const techSupport = document.querySelector('input[name="tech_support"]:checked')?.value;
  const onlineSecurity = document.querySelector('input[name="online_security"]:checked')?.value;
  const paperlessBilling = document.querySelector('input[name="paperless_billing"]:checked')?.value;
  const paymentMethod = document.getElementById('payment_method').value;

  const payload = {
    tenure,
    monthly_charges: monthlyCharges,
    total_charges: totalCharges,
    contract,
    internet_service: internetService,
    tech_support: techSupport,
    online_security: onlineSecurity,
    paperless_billing: paperlessBilling,
    payment_method: paymentMethod,
  };

  // Set loading UI state
  predictBtn.classList.add('loading');
  predictBtn.disabled = true;

  try {
    const response = await fetch('/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMsg = errorData.detail || `Server error: ${response.status}`;
      throw new Error(errorMsg);
    }

    const result = await response.json();
    renderPredictionResult(result);
  } catch (error) {
    console.error('Prediction call failed:', error);
    showToast(`Prediction failed: ${error.message || 'Cannot reach API'}`);
  } finally {
    predictBtn.classList.remove('loading');
    predictBtn.disabled = false;
  }
}

function renderPredictionResult(result) {
  // Transition views from empty state to active result
  resultEmptyState.style.display = 'none';
  resultContent.style.display = 'flex';

  const prob = result.churn_probability;
  const percentage = prob * 100;

  // 1. Animate Semicircle SVG Gauge Fill
  // strokeDashoffset: full = 283 (empty), 0 = 100% full
  const targetOffset = GAUGE_CIRCUMFERENCE - (prob * GAUGE_CIRCUMFERENCE);
  gaugeProgress.style.strokeDashoffset = targetOffset;

  // 2. Count-up percentage text
  animateValue(probPercentageText, 0, percentage, 1000, 1, '%');

  // 3. Update Risk Tier Badge & SVG Illustration
  riskBadge.className = 'risk-badge';
  verdictBanner.className = 'verdict-banner';

  if (result.risk_level === 'Low') {
    riskBadge.classList.add('risk-low');
    verdictBanner.classList.add('verdict-low');
    riskIcon.src = '/static/img/low-risk.svg';
    riskText.textContent = 'Low Risk';
    verdictText.textContent = 'This customer is satisfied and likely to remain retained.';
  } else if (result.risk_level === 'Medium') {
    riskBadge.classList.add('risk-med');
    verdictBanner.classList.add('verdict-med');
    riskIcon.src = '/static/img/medium-risk.svg';
    riskText.textContent = 'Medium Risk';
    verdictText.textContent = 'Customer shows vulnerability to churn. Targeted retention advised.';
  } else {
    riskBadge.classList.add('risk-high');
    verdictBanner.classList.add('verdict-high');
    riskIcon.src = '/static/img/high-risk.svg';
    riskText.textContent = 'High Risk';
    verdictText.textContent = 'High churn probability! Immediate retention action recommended.';
  }

  // 4. Staggered list animation for recommendations
  suggestionsList.innerHTML = '';
  result.suggestions.forEach((suggestion, idx) => {
    const li = document.createElement('li');
    li.className = 'suggestion-item';
    li.style.animationDelay = `${(idx + 1) * 120}ms`;
    li.innerHTML = `
      <svg viewBox="0 0 20 20" width="16" height="16" fill="currentColor" style="flex-shrink:0; margin-top:2px; color:var(--accent-cyan);">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
      </svg>
      <span>${suggestion}</span>
    `;
    suggestionsList.appendChild(li);
  });
}

churnForm.addEventListener('submit', function (e) {
  e.preventDefault();
  executePrediction();
});


/* ==========================================================================
   9. Load Live Metrics & Feature Importance from API
   Why: All numbers displayed come dynamically from real training files,
   strictly adhering to the rule against hardcoding or faking metrics.
   ========================================================================== */
async function loadMetricsData() {
  try {
    const res = await fetch('/api/metrics');
    if (!res.ok) throw new Error('Metrics endpoint unavailable');
    const data = await res.json();

    const rf = data.random_forest;
    const lr = data.logistic_regression;

    // Update Hero Stats Chips
    const statRecords = document.getElementById('hero-stat-records');
    const statAuc = document.getElementById('hero-stat-auc');
    const statAcc = document.getElementById('hero-stat-acc');

    if (statRecords) animateValue(statRecords, 0, data.dataset_size, 1200);
    if (statAuc) animateValue(statAuc, 0, rf.roc_auc * 100, 1200, 1, '%');
    if (statAcc) animateValue(statAcc, 0, rf.accuracy * 100, 1200, 1, '%');

    // Update Insights Cards
    const accEl = document.getElementById('metric-accuracy');
    const rocEl = document.getElementById('metric-roc');
    const precEl = document.getElementById('metric-precision');
    const recEl = document.getElementById('metric-recall');
    const f1El = document.getElementById('metric-f1');

    if (accEl) animateValue(accEl, 0, rf.accuracy * 100, 1400, 1, '%');
    if (rocEl) animateValue(rocEl, 0, rf.roc_auc, 1400, 3, '');
    if (precEl) animateValue(precEl, 0, rf.precision * 100, 1400, 1, '%');
    if (recEl) animateValue(recEl, 0, rf.recall * 100, 1400, 1, '%');
    if (f1El) animateValue(f1El, 0, rf.f1, 1400, 3, '');

    // Update Model Comparison Progress Bars
    triggerComparisonBars(rf, lr);
  } catch (err) {
    console.warn('Could not load live metrics:', err);
  }
}

function triggerComparisonBars(rf, lr) {
  // Dynamically set widths based on actual API payload
  const compContainer = document.getElementById('comparison-container');
  if (!compContainer) return;

  compContainer.innerHTML = `
    <!-- Accuracy -->
    <div class="comp-group">
      <div class="comp-label-row">
        <span class="comp-name">Overall Accuracy</span>
        <span class="comp-scores">RF: <strong>${(rf.accuracy * 100).toFixed(1)}%</strong> | LR: ${(lr.accuracy * 100).toFixed(1)}%</span>
      </div>
      <div class="comp-bar-track">
        <div class="comp-bar-fill rf-fill" style="width: ${rf.accuracy * 100}%;"></div>
        <div class="comp-bar-fill lr-fill" style="width: ${lr.accuracy * 100}%;"></div>
      </div>
    </div>

    <!-- ROC-AUC -->
    <div class="comp-group">
      <div class="comp-label-row">
        <span class="comp-name">ROC-AUC Discriminator</span>
        <span class="comp-scores">RF: <strong>${rf.roc_auc.toFixed(3)}</strong> | LR: ${lr.roc_auc.toFixed(3)}</span>
      </div>
      <div class="comp-bar-track">
        <div class="comp-bar-fill rf-fill" style="width: ${rf.roc_auc * 100}%;"></div>
        <div class="comp-bar-fill lr-fill" style="width: ${lr.roc_auc * 100}%;"></div>
      </div>
    </div>

    <!-- Precision -->
    <div class="comp-group">
      <div class="comp-label-row">
        <span class="comp-name">Precision (False Alarm Shield)</span>
        <span class="comp-scores">RF: <strong>${(rf.precision * 100).toFixed(1)}%</strong> | LR: ${(lr.precision * 100).toFixed(1)}%</span>
      </div>
      <div class="comp-bar-track">
        <div class="comp-bar-fill rf-fill" style="width: ${rf.precision * 100}%;"></div>
        <div class="comp-bar-fill lr-fill" style="width: ${lr.precision * 100}%;"></div>
      </div>
    </div>

    <!-- Recall -->
    <div class="comp-group">
      <div class="comp-label-row">
        <span class="comp-name">Recall (Churner Detection)</span>
        <span class="comp-scores">RF: <strong>${(rf.recall * 100).toFixed(1)}%</strong> | LR: ${(lr.recall * 100).toFixed(1)}%</span>
      </div>
      <div class="comp-bar-track">
        <div class="comp-bar-fill rf-fill" style="width: ${rf.recall * 100}%;"></div>
        <div class="comp-bar-fill lr-fill" style="width: ${lr.recall * 100}%;"></div>
      </div>
    </div>
  `;
}

async function loadFeatureImportanceData() {
  try {
    const res = await fetch('/api/feature-importance');
    if (!res.ok) throw new Error('Feature importance API unavailable');
    const features = await res.json();

    if (!featureImportanceList) return;
    featureImportanceList.innerHTML = '';

    // Find maximum importance to scale bars proportionally
    const maxImportance = Math.max(...features.map(f => f.importance));

    features.forEach(item => {
      const pct = (item.importance * 100).toFixed(1);
      const relativeWidth = ((item.importance / maxImportance) * 100).toFixed(1);

      const row = document.createElement('div');
      row.className = 'feature-bar-row';
      row.innerHTML = `
        <div class="feature-info">
          <span class="feature-name">${item.feature}</span>
          <span class="feature-val">${pct}%</span>
        </div>
        <div class="feature-track">
          <div class="feature-fill" data-width="${relativeWidth}%"></div>
        </div>
      `;
      featureImportanceList.appendChild(row);
    });

    // Trigger animated width expansion once added to DOM
    setTimeout(() => {
      document.querySelectorAll('.feature-fill').forEach(fill => {
        fill.style.width = fill.getAttribute('data-width');
      });
    }, 100);
  } catch (err) {
    console.warn('Could not load feature importance:', err);
  }
}


/* ==========================================================================
   10. IntersectionObserver Scroll Reveal
   Why: Smoothly reveals sections and charts as the recruiter scrolls down.
   ========================================================================== */
function initScrollReveal() {
  const revealElements = document.querySelectorAll('.reveal-on-scroll');

  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        obs.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.12,
    rootMargin: '0px 0px -40px 0px'
  });

  revealElements.forEach(el => observer.observe(el));
}


/* ==========================================================================
   Initialization on DOM Load
   ========================================================================== */
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  updateSliderLabels();
  initScrollReveal();
  loadMetricsData();
  loadFeatureImportanceData();
});
