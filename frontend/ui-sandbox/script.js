'use strict';

/* ============================================================
   AUTH UI — script.js
   Two account types share these forms: Public/Citizen (fast,
   passwordless, mobile+OTP) and Official/Institutional (strict
   verification, password + mandatory MFA). Both field sets live
   in the DOM at once; only one is shown at a time based on
   [data-user-type] on #authCard (see the .citizen-only /
   .official-only CSS rules in style.css).
   ============================================================ */
(function () {

  /* ----------------------------------------------------------
     1. DOM REFERENCES
     ---------------------------------------------------------- */
  const authCard = document.getElementById('authCard');
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

  const typeCitizenBtn = document.getElementById('typeCitizen');
  const typeOfficialBtn = document.getElementById('typeOfficial');
  const userTypeIndicator = document.getElementById('userTypeIndicator');

  // Panels in slide order — index maps directly to track translateX steps
  const PANELS = ['login', 'signup', 'forgot'];
  let currentPanel = 'login';
  let toastTimer = null;

  /* ----------------------------------------------------------
     2. THEME (DARK / LIGHT)
     ---------------------------------------------------------- */
  const THEME_KEY = 'theme';
  const root = document.documentElement;

  function getStoredTheme() {
    try { return localStorage.getItem(THEME_KEY); } catch (e) { return null; }
  }

  function storeTheme(theme) {
    try { localStorage.setItem(THEME_KEY, theme); } catch (e) { /* private browsing, etc. */ }
  }

  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    const isLight = theme === 'light';
    themeToggle.setAttribute('aria-pressed', String(isLight));
    themeToggle.setAttribute('aria-label', isLight ? 'Switch to dark theme' : 'Switch to light theme');
  }

  applyTheme(root.getAttribute('data-theme') || 'dark');

  themeToggle.addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
    applyTheme(next);
    storeTheme(next);
  });

  if (window.matchMedia) {
    const mql = window.matchMedia('(prefers-color-scheme: light)');
    const onSystemThemeChange = (e) => {
      if (getStoredTheme()) return;
      applyTheme(e.matches ? 'light' : 'dark');
    };
    if (mql.addEventListener) mql.addEventListener('change', onSystemThemeChange);
    else if (mql.addListener) mql.addListener(onSystemThemeChange);
  }

  /* ----------------------------------------------------------
     3. ACCOUNT TYPE (citizen / official)
     ---------------------------------------------------------- */
  function setUserType(type) {
    authCard.setAttribute('data-user-type', type);

    const isOfficial = type === 'official';
    typeCitizenBtn.classList.toggle('is-active', !isOfficial);
    typeOfficialBtn.classList.toggle('is-active', isOfficial);
    typeCitizenBtn.setAttribute('aria-selected', String(!isOfficial));
    typeOfficialBtn.setAttribute('aria-selected', String(isOfficial));
    userTypeIndicator.classList.toggle('is-official', isOfficial);

    // Switching account type mid-flow would mix incompatible
    // fields, so reset both forms back to their first step.
    goToStep(loginForm, 1);
    goToStep(signupForm, 1);
    updateLoginSubmitLabel();
    updateSignupSubmitLabel();
    syncViewportHeight();
  }

  typeCitizenBtn.addEventListener('click', () => setUserType('citizen'));
  typeOfficialBtn.addEventListener('click', () => setUserType('official'));

  function currentUserType() {
    return authCard.getAttribute('data-user-type') === 'official' ? 'official' : 'citizen';
  }

  /* ----------------------------------------------------------
     4. VALIDATION RULES
     ---------------------------------------------------------- */
  const patterns = {
    mobile: /^[6-9]\d{9}$/, // Indian 10-digit mobile numbers
    email: /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/,
    officialEmail: /@([a-z0-9-]+\.)*(gov\.in|nic\.in)$/i,
    otp: /^\d{6}$/,
    pincode: /^\d{6}$/,
  };

  const validators = {
    // ---- Citizen login ----
    citizenLoginMobile(value) {
      if (!value.trim()) return 'Enter your mobile number.';
      if (!patterns.mobile.test(value.trim())) return 'Enter a valid 10-digit mobile number.';
      return '';
    },

    // ---- Official login ----
    officialLoginIdentifier(value) {
      if (!value.trim()) return 'Enter your official email or username.';
      return '';
    },
    officialLoginPassword(value) {
      if (!value) return 'Enter your password.';
      return '';
    },

    // ---- Shared OTP / MFA field (context depends on step + user type) ----
    loginOtp(value) {
      if (!value.trim()) return 'Enter the code.';
      if (!patterns.otp.test(value.trim())) return 'Enter the 6-digit code.';
      return '';
    },

    // ---- Citizen signup ----
    citizenSignupMobile(value) {
      if (!value.trim()) return 'Enter your mobile number.';
      if (!patterns.mobile.test(value.trim())) return 'Enter a valid 10-digit mobile number.';
      return '';
    },
    citizenSignupPincode(value) {
      if (!value.trim()) return 'Enter your PIN code.';
      if (!patterns.pincode.test(value.trim())) return 'Enter a valid 6-digit PIN code.';
      return '';
    },
    citizenSignupLanguage(value) {
      if (!value) return 'Select your preferred language.';
      return '';
    },
    citizenSignupOtp(value) {
      if (!value.trim()) return 'Enter the code.';
      if (!patterns.otp.test(value.trim())) return 'Enter the 6-digit code.';
      return '';
    },

    // ---- Official signup ----
    officialSignupName(value) {
      if (!value.trim()) return 'Enter your full name.';
      return '';
    },
    officialSignupDesignation(value) {
      if (!value.trim()) return 'Enter your designation.';
      return '';
    },
    officialSignupEmail(value) {
      if (!value.trim()) return 'Enter your official email address.';
      if (!patterns.email.test(value.trim())) return 'Enter a valid email address.';
      if (!patterns.officialEmail.test(value.trim())) return 'Use an official @gov.in or @nic.in address.';
      return '';
    },
    officialSignupMobile(value) {
      if (!value.trim()) return 'Enter your official mobile number.';
      if (!patterns.mobile.test(value.trim())) return 'Enter a valid 10-digit mobile number.';
      return '';
    },
    officialSignupGovId(value) {
      if (!value.trim()) return 'Enter your Government/Agency ID.';
      return '';
    },
    officialSignupIdProof(value) {
      if (!value) return 'Upload a copy of your ID proof.';
      return '';
    },
    officialSignupState(value) {
      if (!value) return 'Select your state or UT.';
      return '';
    },
    officialSignupDistrict(value) {
      if (!value.trim()) return 'Enter your district.';
      return '';
    },
    officialSignupBlockCode(value) {
      if (!value.trim()) return 'Enter your block code.';
      return '';
    },
    officialSignupDept(value) {
      if (!value) return 'Select your department.';
      return '';
    },
    officialSignupDeptOther(value, form) {
      const dept = form.querySelector('#officialSignupDept');
      if (dept && dept.value === 'other' && !value.trim()) {
        return 'Specify your department.';
      }
      return '';
    },
    officialSignupPassword(value) {
      if (!value) return 'Create a password.';
      if (value.length < 8) return 'Password must be at least 8 characters.';
      if (!/[a-z]/.test(value) || !/[A-Z]/.test(value)) {
        return 'Include both uppercase and lowercase letters.';
      }
      if (!/[0-9]/.test(value)) return 'Include at least one number.';
      return '';
    },
    officialSignupConfirmPassword(value, form) {
      const pwd = form.querySelector('#officialSignupPassword').value;
      if (!value) return 'Re-enter your password.';
      if (value !== pwd) return 'Passwords do not match.';
      return '';
    },

    // ---- Forgot password (official only) ----
    forgotEmail(value) {
      if (!value.trim()) return 'Enter your official email address.';
      if (!patterns.email.test(value.trim())) return 'Enter a valid email address.';
      return '';
    },
  };

  /* ----------------------------------------------------------
     5. FIELD ACTIVITY
     A field only needs validating when it's actually visible:
     matches the current account type AND its step isn't hidden.
     ---------------------------------------------------------- */
  function isFieldActive(input) {
    if (input.disabled) return false;
    if (input.closest('[hidden]')) return false;

    const roleWrap = input.closest('.citizen-only, .official-only');
    if (roleWrap) {
      const isCitizenField = roleWrap.classList.contains('citizen-only');
      const type = currentUserType();
      if (isCitizenField && type !== 'citizen') return false;
      if (!isCitizenField && type !== 'official') return false;
    }
    return true;
  }

  /* ----------------------------------------------------------
     6. FIELD ERROR HELPERS
     ---------------------------------------------------------- */
  function setFieldState(input, message) {
    const field = input.closest('.field');
    if (!field) return;
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
      if (input.value.trim()) field.classList.add('is-valid');
      else field.classList.remove('is-valid');
      input.removeAttribute('aria-invalid');
    }
  }

  function validateField(input, form) {
    const rule = validators[input.id];
    if (!rule) return true;
    const message = rule(input.value, form);
    setFieldState(input, message);
    return !message;
  }

  /* ----------------------------------------------------------
     7. LIVE VALIDATION
     ---------------------------------------------------------- */
  function attachLiveValidation(form) {
    form.querySelectorAll('input[id], select[id]').forEach((input) => {
      if (!validators[input.id]) return;
      const evt = input.tagName === 'SELECT' ? 'change' : 'input';
      input.addEventListener(evt, () => {
        validateField(input, form);
        if (input.id === 'officialSignupPassword') {
          const confirm = form.querySelector('#officialSignupConfirmPassword');
          if (confirm && confirm.value) validateField(confirm, form);
        }
      });
      if (evt === 'input') input.addEventListener('blur', () => validateField(input, form));
    });
  }
  attachLiveValidation(loginForm);
  attachLiveValidation(signupForm);
  attachLiveValidation(forgotForm);

  function validateStep(form, stepPanel) {
    const inputs = Array.from(stepPanel.querySelectorAll('input[id], select[id]'))
      .filter((i) => validators[i.id])
      .filter(isFieldActive);
    let allValid = true;
    inputs.forEach((input) => {
      if (!validateField(input, form)) allValid = false;
    });
    return allValid;
  }

  /* ----------------------------------------------------------
     8. PASSWORD STRENGTH METER (official signup only)
     ---------------------------------------------------------- */
  const strengthMeter = document.getElementById('strengthMeter');
  const strengthLabel = document.getElementById('strengthLabel');
  const strengthBars = strengthMeter.querySelectorAll('.strength__bar i');
  const officialSignupPasswordInput = document.getElementById('officialSignupPassword');

  function scorePassword(value) {
    if (!value) return 0;
    let score = 0;
    if (value.length >= 8) score++;
    if (value.length >= 12) score++;
    if (/[a-z]/.test(value) && /[A-Z]/.test(value)) score++;
    if (/[0-9]/.test(value)) score++;
    if (/[^A-Za-z0-9]/.test(value)) score++;
    return score;
  }

  function updateStrengthMeter(value) {
    const score = scorePassword(value);
    let level = '';
    let filled = 0;
    let color = 'var(--text-faint)';

    if (!value) {
      level = ''; filled = 0;
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

  officialSignupPasswordInput.addEventListener('input', (e) => updateStrengthMeter(e.target.value));

  /* ----------------------------------------------------------
     9. SHOW / HIDE PASSWORD
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
     10. FILE UPLOAD — show the chosen filename
     ---------------------------------------------------------- */
  const idProofInput = document.getElementById('officialSignupIdProof');
  const idProofName = document.getElementById('officialSignupIdProofName');

  idProofInput.addEventListener('change', () => {
    const file = idProofInput.files && idProofInput.files[0];
    idProofName.textContent = file ? file.name : 'No file chosen';
    idProofName.classList.toggle('has-file', Boolean(file));
    validateField(idProofInput, signupForm);
  });

  /* ----------------------------------------------------------
     11. DEPARTMENT "OTHER" REVEAL
     ---------------------------------------------------------- */
  const deptSelect = document.getElementById('officialSignupDept');
  const deptOtherField = document.getElementById('officialSignupDeptOtherField');
  const deptOtherInput = document.getElementById('officialSignupDeptOther');

  deptSelect.addEventListener('change', () => {
    const isOther = deptSelect.value === 'other';
    deptOtherField.hidden = !isOther;
    if (!isOther) setFieldState(deptOtherInput, '');
    syncViewportHeight();
  });

  /* ----------------------------------------------------------
     12. MFA METHOD (official login, step 2) — relabels the
     shared OTP field and hides the resend link for TOTP, since
     an authenticator code isn't something we send.
     ---------------------------------------------------------- */
  const loginOtpLabel = document.getElementById('loginOtpLabel');
  const loginOtpInput = document.getElementById('loginOtp');
  const loginResendRow = document.getElementById('loginResendRow');

  document.querySelectorAll('input[name="loginMfaMethod"]').forEach((radio) => {
    radio.addEventListener('change', () => {
      const isTotp = radio.value === 'totp' && radio.checked;
      if (radio.checked) {
        loginOtpLabel.textContent = isTotp ? 'Authenticator code' : 'One-time code';
        loginOtpInput.placeholder = isTotp ? '••••••' : '••••••';
        loginResendRow.querySelector('#loginResendOtp').hidden = isTotp;
      }
    });
  });

  /* ----------------------------------------------------------
     13. PANEL / TAB NAVIGATION
     ---------------------------------------------------------- */
  function panelHeight(panel) {
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

    const activeEl = { login: loginPanel, signup: signupPanel, forgot: forgotPanel }[name];
    const firstVisibleInput = Array.from(activeEl.querySelectorAll('input, select'))
      .find((el) => isFieldActive(el) && el.offsetParent !== null);
    if (firstVisibleInput) {
      window.setTimeout(() => firstVisibleInput.focus({ preventScroll: true }), 200);
    }
  }

  tabLogin.addEventListener('click', () => goToPanel('login'));
  tabSignup.addEventListener('click', () => goToPanel('signup'));
  forgotBtn.addEventListener('click', () => goToPanel('forgot'));

  document.querySelectorAll('[data-goto]').forEach((btn) => {
    btn.addEventListener('click', () => goToPanel(btn.getAttribute('data-goto')));
  });

  window.addEventListener('resize', syncViewportHeight);

  /* ----------------------------------------------------------
     14. STEP NAVIGATION (within login / signup forms)
     ---------------------------------------------------------- */
  function goToStep(form, stepNumber) {
    form.dataset.step = String(stepNumber);
    form.querySelectorAll('.form-step').forEach((panel) => {
      panel.hidden = Number(panel.dataset.stepPanel) !== stepNumber;
    });
    syncViewportHeight();
  }

  function updateLoginSubmitLabel() {
    const label = document.getElementById('loginSubmitLabel');
    label.textContent = currentUserType() === 'official' ? 'Continue' : 'Send OTP';
  }

  function updateSignupSubmitLabel() {
    const label = document.getElementById('signupSubmitLabel');
    label.textContent = currentUserType() === 'official' ? 'Submit for Verification' : 'Send OTP';
  }

  updateLoginSubmitLabel();
  updateSignupSubmitLabel();

  /* ----------------------------------------------------------
     15. RESEND COUNTDOWN
     ---------------------------------------------------------- */
  function startResendCountdown(button, seconds = 30) {
    if (button.hidden) return;
    let remaining = seconds;
    button.disabled = true;
    const originalText = 'Resend code';
    button.textContent = `Resend in ${remaining}s`;

    const timer = window.setInterval(() => {
      remaining -= 1;
      if (remaining <= 0) {
        window.clearInterval(timer);
        button.disabled = false;
        button.textContent = originalText;
      } else {
        button.textContent = `Resend in ${remaining}s`;
      }
    }, 1000);
  }

  /* ----------------------------------------------------------
     16. SESSION METADATA (official login)
     Real device/IP/location logging happens server-side. This
     just captures what's available client-side so the payload
     sent at login has something meaningful in it.
     ---------------------------------------------------------- */
  function collectSessionMetadata() {
    const metadata = {
      userAgent: navigator.userAgent,
      timestamp: new Date().toISOString(),
      // IP address is only known server-side from the request.
      // GPS is only requested if the browser already has permission —
      // we never prompt for it silently.
    };
    if (navigator.geolocation && navigator.permissions) {
      navigator.permissions.query({ name: 'geolocation' }).then((status) => {
        if (status.state === 'granted') {
          navigator.geolocation.getCurrentPosition((pos) => {
            metadata.gps = { lat: pos.coords.latitude, lng: pos.coords.longitude };
          }, () => {}, { timeout: 2000 });
        }
      }).catch(() => {});
    }
    return metadata;
  }

  /* ----------------------------------------------------------
     17. TOAST NOTIFICATIONS
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
     18. SUBMIT BUTTON LOADING STATE
     ---------------------------------------------------------- */
  function setLoading(button, isLoading) {
    button.classList.toggle('is-loading', isLoading);
    button.disabled = isLoading;
  }

  function simulateRequest(ms = 1100) {
    return new Promise((resolve) => window.setTimeout(resolve, ms));
  }

  function shakeCard() {
    const card = document.getElementById('authCard');
    card.classList.remove('shake');
    void card.offsetWidth;
    card.classList.add('shake');
  }

  /* ----------------------------------------------------------
     19. LOGIN FORM
     Citizen: mobile -> OTP -> logged in.
     Official: email+password -> MFA (OTP or TOTP) -> logged in.
     ---------------------------------------------------------- */
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const step = Number(loginForm.dataset.step);
    const type = currentUserType();

    if (step === 1) {
      const step1Panel = loginForm.querySelector('[data-step-panel="1"]');
      if (!validateStep(loginForm, step1Panel)) {
        shakeCard();
        return;
      }

      const submitBtn = document.getElementById('loginSubmit');
      setLoading(submitBtn, true);
      await simulateRequest(type === 'citizen' ? 900 : 700);
      setLoading(submitBtn, false);

      if (type === 'citizen') {
        const mobile = document.getElementById('citizenLoginMobile').value.trim();
        document.getElementById('citizenLoginMobileDisplay').textContent = mobile;
        showToast('OTP sent to your mobile number.');
      } else {
        showToast('Credentials verified. Complete MFA to continue.');
      }

      goToStep(loginForm, 2);
      startResendCountdown(document.getElementById('loginResendOtp'));
      const otpField = document.getElementById('loginOtp');
      window.setTimeout(() => otpField.focus({ preventScroll: true }), 200);
      return;
    }

    // Step 2 — verify OTP / MFA code
    const step2Panel = loginForm.querySelector('[data-step-panel="2"]');
    if (!validateStep(loginForm, step2Panel)) {
      shakeCard();
      return;
    }

    const verifyBtn = document.getElementById('loginVerifySubmit');
    setLoading(verifyBtn, true);
    await simulateRequest();
    setLoading(verifyBtn, false);

    if (type === 'official') {
      const metadata = collectSessionMetadata();
      try { localStorage.setItem('sessionMetadata', JSON.stringify(metadata)); } catch (err) { /* no-op */ }
    }

    const remembered = document.getElementById('rememberMe').checked;
    showToast(`Welcome back! You're logged in${type === 'official' && remembered ? ' — we\'ll remember you' : ''}.`);

    loginForm.reset();
    loginForm.querySelectorAll('.field').forEach((f) => f.classList.remove('is-valid', 'is-invalid'));
    goToStep(loginForm, 1);
  });

  document.getElementById('loginBackStep').addEventListener('click', () => {
    goToStep(loginForm, 1);
  });

  document.getElementById('loginResendOtp').addEventListener('click', (e) => {
    showToast('A new code is on its way.');
    startResendCountdown(e.currentTarget);
  });

  /* ----------------------------------------------------------
     20. SIGNUP FORM
     Citizen: details -> OTP -> account created.
     Official: full form -> submitted for manual verification
     (no OTP step — a human reviews the uploaded ID proof).
     ---------------------------------------------------------- */
  signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const step = Number(signupForm.dataset.step);
    const type = currentUserType();

    if (step === 1) {
      const step1Panel = signupForm.querySelector('[data-step-panel="1"]');
      if (!validateStep(signupForm, step1Panel)) {
        shakeCard();
        return;
      }

      const submitBtn = document.getElementById('signupSubmit');
      setLoading(submitBtn, true);
      await simulateRequest(type === 'citizen' ? 900 : 1400);
      setLoading(submitBtn, false);

      if (type === 'official') {
        showToast("Submitted! You'll get a confirmation email once your account is verified.");
        signupForm.reset();
        signupForm.querySelectorAll('.field').forEach((f) => f.classList.remove('is-valid', 'is-invalid'));
        updateStrengthMeter('');
        idProofName.textContent = 'No file chosen';
        idProofName.classList.remove('has-file');
        deptOtherField.hidden = true;
        goToStep(signupForm, 1);
        goToPanel('login');
        return;
      }

      // Citizen — move to OTP verification
      const mobile = document.getElementById('citizenSignupMobile').value.trim();
      document.getElementById('citizenSignupMobileDisplay').textContent = mobile;
      showToast('OTP sent to your mobile number.');
      goToStep(signupForm, 2);
      startResendCountdown(document.getElementById('signupResendOtp'));
      const otpField = document.getElementById('citizenSignupOtp');
      window.setTimeout(() => otpField.focus({ preventScroll: true }), 200);
      return;
    }

    // Step 2 — citizen OTP verification
    const step2Panel = signupForm.querySelector('[data-step-panel="2"]');
    if (!validateStep(signupForm, step2Panel)) {
      shakeCard();
      return;
    }

    const verifyBtn = document.getElementById('signupVerifySubmit');
    setLoading(verifyBtn, true);
    await simulateRequest();
    setLoading(verifyBtn, false);

    showToast('Account created! You can log in now.');
    signupForm.reset();
    signupForm.querySelectorAll('.field').forEach((f) => f.classList.remove('is-valid', 'is-invalid'));
    goToStep(signupForm, 1);
    goToPanel('login');
  });

  document.getElementById('signupBackStep').addEventListener('click', () => {
    goToStep(signupForm, 1);
  });

  document.getElementById('signupResendOtp').addEventListener('click', (e) => {
    showToast('A new code is on its way.');
    startResendCountdown(e.currentTarget);
  });

  /* ----------------------------------------------------------
     21. FORGOT PASSWORD (official accounts only)
     ---------------------------------------------------------- */
  forgotForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const forgotEmailInput = document.getElementById('forgotEmail');
    if (!validateField(forgotEmailInput, forgotForm)) {
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
     22. INITIAL STATE
     Honour a deep link like index.html#signup, and default to
     the citizen flow (lower friction, larger audience).
     ---------------------------------------------------------- */
  setUserType('citizen');
  const requestedPanel = window.location.hash.replace('#', '');
  goToPanel(PANELS.includes(requestedPanel) ? requestedPanel : 'login');

})();