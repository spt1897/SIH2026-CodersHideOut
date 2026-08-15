'use strict';

/* ============================================================
   AUTH UI — script.js
   All logic is namespaced inside an IIFE to avoid leaking
   globals. No framework, no build step — just DOM + events.
   ============================================================ */
(function () {

  /* ----------------------------------------------------------
     1. DOM REFERENCES
     ---------------------------------------------------------- */
  const viewport = document.getElementById('viewport');
  const track = document.getElementById('track');

  const tabLogin = document.getElementById('tabLogin');
  const tabSignup = document.getElementById('tabSignup');
  const tabIndicator = document.getElementById('tabIndicator');

  const loginPanel = document.getElementById('loginPanel');
  const signupPanel = document.getElementById('signupPanel');
  const forgotPanel = document.getElementById('forgotPanel');

  const loginForm = document.getElementById('loginForm');
  const signupForm = document.getElementById('signupForm');
  const forgotForm = document.getElementById('forgotForm');

  const forgotBtn = document.getElementById('forgotPasswordBtn');
  const toast = document.getElementById('toast');
  const themeToggle = document.getElementById('themeToggle');

  // Panels in slide order — index maps directly to track translateX steps
  const PANELS = ['login', 'signup', 'forgot'];
  let currentPanel = 'login';
  let toastTimer = null;

  /* ----------------------------------------------------------
     2. THEME (DARK / LIGHT)
     The <head> already sets data-theme on <html> before first
     paint (see the inline script in index.html) so there's no
     flash. This section just wires up the toggle button and
     keeps the choice in sync with localStorage + the OS-level
     preference for tabs where the user hasn't chosen yet.
     ---------------------------------------------------------- */
  const THEME_KEY = 'theme';
  const root = document.documentElement;

  function getStoredTheme() {
    try {
      return localStorage.getItem(THEME_KEY);
    } catch (e) {
      return null;
    }
  }

  function storeTheme(theme) {
    try {
      localStorage.setItem(THEME_KEY, theme);
    } catch (e) {
      // localStorage unavailable (private browsing, etc.) — theme
      // still applies for this session, it just won't persist.
    }
  }

  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    const isLight = theme === 'light';
    themeToggle.setAttribute('aria-pressed', String(isLight));
    themeToggle.setAttribute('aria-label', isLight ? 'Switch to dark theme' : 'Switch to light theme');
  }

  // Apply whatever the inline <head> script already set, so the
  // toggle button's aria attributes match what's on screen.
  applyTheme(root.getAttribute('data-theme') || 'dark');

  themeToggle.addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
    applyTheme(next);
    storeTheme(next);
  });

  // If the user hasn't explicitly chosen a theme on this device,
  // follow the OS-level preference live (e.g. it flips at sunset).
  if (window.matchMedia) {
    const mql = window.matchMedia('(prefers-color-scheme: light)');
    const onSystemThemeChange = (e) => {
      if (getStoredTheme()) return; // user has an explicit choice — don't override it
      applyTheme(e.matches ? 'light' : 'dark');
    };
    if (mql.addEventListener) mql.addEventListener('change', onSystemThemeChange);
    else if (mql.addListener) mql.addListener(onSystemThemeChange); // older Safari
  }

  /* ----------------------------------------------------------
     3. VALIDATION RULES
     Centralised so both "live" (on input) and "on submit"
     checks use exactly the same logic.
     ---------------------------------------------------------- */
  const patterns = {
    username: /^[A-Za-z][A-Za-z0-9_]{2,19}$/, // 3-20 chars, starts with a letter
    email: /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/,
  };

  const validators = {
    loginIdentifier(value) {
      if (!value.trim()) return 'Enter your username or email.';
      return '';
    },
    loginPassword(value) {
      if (!value) return 'Enter your password.';
      return '';
    },
    signupUsername(value) {
      if (!value.trim()) return 'Choose a username.';
      if (!patterns.username.test(value)) {
        return 'Use 3–20 characters, starting with a letter (letters, numbers, _).';
      }
      return '';
    },
    signupEmail(value) {
      if (!value.trim()) return 'Enter your email address.';
      if (!patterns.email.test(value)) return 'Enter a valid email address.';
      return '';
    },
    signupPassword(value) {
      if (!value) return 'Create a password.';
      if (value.length < 8) return 'Password must be at least 8 characters.';
      if (!/[a-z]/.test(value) || !/[A-Z]/.test(value)) {
        return 'Include both uppercase and lowercase letters.';
      }
      if (!/[0-9]/.test(value)) return 'Include at least one number.';
      return '';
    },
    signupConfirmPassword(value, form) {
      const pwd = form.querySelector('#signupPassword').value;
      if (!value) return 'Re-enter your password.';
      if (value !== pwd) return 'Passwords do not match.';
      return '';
    },
    forgotEmail(value) {
      if (!value.trim()) return 'Enter your email address.';
      if (!patterns.email.test(value)) return 'Enter a valid email address.';
      return '';
    },
  };

  /* ----------------------------------------------------------
     4. FIELD ERROR HELPERS
     Shows/removes the error message directly under a field and
     toggles valid/invalid styling on the wrapping .field element.
     ---------------------------------------------------------- */
  function setFieldState(input, message) {
    const field = input.closest('.field');
    const errorEl = field.querySelector('.field__error');

    if (message) {
      errorEl.textContent = message;
      errorEl.classList.add('is-visible');
      field.classList.add('is-invalid');
      field.classList.remove('is-valid');
      input.setAttribute('aria-invalid', 'true');
    } else {
      errorEl.textContent = '';
      errorEl.classList.remove('is-visible');
      field.classList.remove('is-invalid');
      // Only mark visibly "valid" once the user has typed something
      if (input.value.trim()) field.classList.add('is-valid');
      else field.classList.remove('is-valid');
      input.removeAttribute('aria-invalid');
    }
  }

  /**
   * Validates one input against its rule, updates its UI, and
   * returns true when the field is valid.
   */
  function validateField(input, form) {
    const rule = validators[input.id];
    if (!rule) return true;
    const message = rule(input.value, form);
    setFieldState(input, message);
    return !message;
  }

  /* ----------------------------------------------------------
     5. LIVE VALIDATION — wire up "input" listeners
     ---------------------------------------------------------- */
  function attachLiveValidation(form) {
    form.querySelectorAll('input[id]').forEach((input) => {
      if (!validators[input.id]) return;
      input.addEventListener('input', () => {
        validateField(input, form);
        // Re-check confirm-password whenever the primary password changes
        if (input.id === 'signupPassword') {
          const confirm = form.querySelector('#signupConfirmPassword');
          if (confirm && confirm.value) validateField(confirm, form);
        }
      });
      input.addEventListener('blur', () => validateField(input, form));
    });
  }
  attachLiveValidation(loginForm);
  attachLiveValidation(signupForm);
  attachLiveValidation(forgotForm);

  /* ----------------------------------------------------------
     6. PASSWORD STRENGTH METER
     ---------------------------------------------------------- */
  const strengthMeter = document.getElementById('strengthMeter');
  const strengthLabel = document.getElementById('strengthLabel');
  const strengthBars = strengthMeter.querySelectorAll('.strength__bar i');
  const signupPasswordInput = document.getElementById('signupPassword');

  function scorePassword(value) {
    if (!value) return 0;
    let score = 0;
    if (value.length >= 8) score++;
    if (value.length >= 12) score++;
    if (/[a-z]/.test(value) && /[A-Z]/.test(value)) score++;
    if (/[0-9]/.test(value)) score++;
    if (/[^A-Za-z0-9]/.test(value)) score++;
    return score; // 0–5
  }

  function updateStrengthMeter(value) {
    const score = scorePassword(value);
    let level = '';
    let filled = 0;
    let color = 'var(--text-faint)';

    if (!value) {
      level = '';
      filled = 0;
    } else if (score <= 2) {
      level = 'weak'; filled = 1; color = 'var(--danger)';
    } else if (score <= 4) {
      level = 'medium'; filled = 2; color = 'var(--warn)';
    } else {
      level = 'strong'; filled = 3; color = 'var(--success)';
    }

    strengthBars.forEach((bar, i) => {
      bar.style.width = i < filled ? '100%' : '0%';
      bar.style.background = i < filled ? color : 'var(--text-faint)';
    });

    strengthLabel.textContent = value
      ? `Password strength: ${level.charAt(0).toUpperCase() + level.slice(1)}`
      : '';
    if (level) strengthLabel.setAttribute('data-level', level);
    else strengthLabel.removeAttribute('data-level');
  }

  signupPasswordInput.addEventListener('input', (e) => updateStrengthMeter(e.target.value));

  /* ----------------------------------------------------------
     7. SHOW / HIDE PASSWORD
     ---------------------------------------------------------- */
  document.querySelectorAll('.eye-toggle').forEach((btn) => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-target');
      const input = document.getElementById(targetId);
      const openIcon = btn.querySelector('.eye-open');
      const closedIcon = btn.querySelector('.eye-closed');

      const isHidden = input.type === 'password';
      input.type = isHidden ? 'text' : 'password';

      openIcon.hidden = isHidden;
      closedIcon.hidden = !isHidden;
      btn.setAttribute('aria-pressed', String(isHidden));
      btn.setAttribute('aria-label', isHidden ? 'Hide password' : 'Show password');
    });
  });

  /* ----------------------------------------------------------
     8. PANEL / TAB NAVIGATION
     Handles the sliding track, the pill indicator, and the
     viewport height animation (panels have different heights).
     ---------------------------------------------------------- */
  function panelHeight(panel) {
    // Measure natural height even while off-screen
    return panel.scrollHeight;
  }

  function syncViewportHeight() {
    const el = { login: loginPanel, signup: signupPanel, forgot: forgotPanel }[currentPanel];
    viewport.style.height = panelHeight(el) + 'px';
  }

  function goToPanel(name) {
    currentPanel = name;
    const index = PANELS.indexOf(name);
    track.style.transform = `translateX(-${index * (100 / 3)}%)`;
    syncViewportHeight();

    const isSignup = name === 'signup';
    const isLogin = name === 'login';

    tabLogin.classList.toggle('is-active', isLogin);
    tabSignup.classList.toggle('is-active', isSignup);
    tabLogin.setAttribute('aria-selected', String(isLogin));
    tabSignup.setAttribute('aria-selected', String(isSignup));
    tabIndicator.classList.toggle('is-signup', isSignup);

    // Move focus to the new panel's first field for keyboard users
    const activeEl = { login: loginPanel, signup: signupPanel, forgot: forgotPanel }[name];
    const firstInput = activeEl.querySelector('input');
    if (firstInput) {
      // Wait for the slide animation so focus doesn't jerk the scroll
      window.setTimeout(() => firstInput.focus({ preventScroll: true }), 200);
    }
  }

  tabLogin.addEventListener('click', () => goToPanel('login'));
  tabSignup.addEventListener('click', () => goToPanel('signup'));
  forgotBtn.addEventListener('click', () => goToPanel('forgot'));

  // Any button with data-goto="login"/"signup" switches panels
  document.querySelectorAll('[data-goto]').forEach((btn) => {
    btn.addEventListener('click', () => goToPanel(btn.getAttribute('data-goto')));
  });

  // Keep the card height correct if the viewport is resized
  // (e.g. rotating a tablet, or a browser zoom change)
  window.addEventListener('resize', syncViewportHeight);

  /* ----------------------------------------------------------
     9. TOAST NOTIFICATIONS
     ---------------------------------------------------------- */
  function showToast(message, duration = 3200) {
    clearTimeout(toastTimer);
    toast.textContent = message;
    toast.classList.add('is-visible');
    toastTimer = window.setTimeout(() => {
      toast.classList.remove('is-visible');
    }, duration);
  }

  /* ----------------------------------------------------------
     10. SUBMIT BUTTON LOADING STATE
     Simulates an async request (e.g. a fetch to a backend).
     Returns a Promise so submit handlers can `await` it.
     ---------------------------------------------------------- */
  function setLoading(button, isLoading) {
    button.classList.toggle('is-loading', isLoading);
    button.disabled = isLoading;
  }

  function simulateRequest(ms = 1100) {
    return new Promise((resolve) => window.setTimeout(resolve, ms));
  }

  /* ----------------------------------------------------------
     11. FORM SUBMIT HANDLERS
     ---------------------------------------------------------- */
  function validateWholeForm(form) {
    const inputs = Array.from(form.querySelectorAll('input[id]')).filter((i) => validators[i.id]);
    let allValid = true;
    inputs.forEach((input) => {
      const valid = validateField(input, form);
      if (!valid) allValid = false;
    });
    return allValid;
  }

  function shakeCard() {
    const card = document.getElementById('authCard');
    card.classList.remove('shake');
    // Force reflow so the animation can re-trigger on repeated invalid attempts
    void card.offsetWidth;
    card.classList.add('shake');
  }

  // ---- Log In ----
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!validateWholeForm(loginForm)) {
      shakeCard();
      return;
    }
    const submitBtn = document.getElementById('loginSubmit');
    setLoading(submitBtn, true);
    await simulateRequest();
    setLoading(submitBtn, false);

    const remembered = document.getElementById('rememberMe').checked;
    showToast(`Welcome back! You're logged in${remembered ? ' — we\'ll remember you' : ''}.`);
    loginForm.reset();
    loginForm.querySelectorAll('.field').forEach((f) => f.classList.remove('is-valid', 'is-invalid'));
  });

  // ---- Sign Up ----
  signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!validateWholeForm(signupForm)) {
      shakeCard();
      return;
    }
    const submitBtn = document.getElementById('signupSubmit');
    setLoading(submitBtn, true);
    await simulateRequest(1300);
    setLoading(submitBtn, false);

    showToast('Account created! You can log in now.');
    signupForm.reset();
    signupForm.querySelectorAll('.field').forEach((f) => f.classList.remove('is-valid', 'is-invalid'));
    updateStrengthMeter('');
    goToPanel('login');
  });

  // ---- Forgot Password ----
  forgotForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!validateWholeForm(forgotForm)) {
      shakeCard();
      return;
    }
    const submitBtn = document.getElementById('forgotSubmit');
    setLoading(submitBtn, true);
    await simulateRequest();
    setLoading(submitBtn, false);

    showToast('If that account exists, a reset link is on its way.');
    forgotForm.reset();
    forgotForm.querySelectorAll('.field').forEach((f) => f.classList.remove('is-valid', 'is-invalid'));
    goToPanel('login');
  });

  /* ----------------------------------------------------------
     12. INITIAL STATE
     ---------------------------------------------------------- */
  goToPanel('login');

})();