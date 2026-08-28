'use strict';

(function () {
  const root = document.documentElement;
  const prefersReducedMotion = window.matchMedia(
    '(prefers-reduced-motion: reduce)'
  ).matches;

  /* ==========================================================
     THEME TOGGLE
     ========================================================== */

  const THEME_KEY = 'theme';
  const themeToggle = document.getElementById('themeToggle');

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
      /* Ignore storage errors */
    }
  }

  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);

    if (!themeToggle) return;

    const isLight = theme === 'light';

    themeToggle.setAttribute(
      'aria-pressed',
      String(isLight)
    );

    themeToggle.setAttribute(
      'aria-label',
      isLight
        ? 'Switch to dark theme'
        : 'Switch to light theme'
    );
  }

  applyTheme(
    root.getAttribute('data-theme') || 'dark'
  );

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const currentTheme =
        root.getAttribute('data-theme') || 'dark';

      const nextTheme =
        currentTheme === 'light'
          ? 'dark'
          : 'light';

      applyTheme(nextTheme);
      storeTheme(nextTheme);
    });
  }

  /* ==========================================================
     SYSTEM THEME CHANGE
     Only changes automatically when the user has not manually
     selected a theme.
     ========================================================== */

  if (window.matchMedia) {
    const mediaQuery = window.matchMedia(
      '(prefers-color-scheme: light)'
    );

    const onSystemThemeChange = (event) => {
      if (getStoredTheme()) return;

      applyTheme(
        event.matches ? 'light' : 'dark'
      );
    };

    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener(
        'change',
        onSystemThemeChange
      );
    } else if (mediaQuery.addListener) {
      mediaQuery.addListener(
        onSystemThemeChange
      );
    }
  }

  /* ==========================================================
     RESPONSIVE MOBILE NAVIGATION
     ========================================================== */

  const navToggle = document.getElementById('navToggle');
  const navLinks = document.getElementById('navLinks');

  function openNav() {
    if (!navToggle || !navLinks) return;

    navLinks.classList.add('is-open');

    navToggle.setAttribute(
      'aria-expanded',
      'true'
    );

    navToggle.setAttribute(
      'aria-label',
      'Close menu'
    );

    document.body.classList.add('menu-open');
  }

  function closeNav() {
    if (!navToggle || !navLinks) return;

    navLinks.classList.remove('is-open');

    navToggle.setAttribute(
      'aria-expanded',
      'false'
    );

    navToggle.setAttribute(
      'aria-label',
      'Open menu'
    );

    document.body.classList.remove('menu-open');
  }

  function toggleNav() {
    if (!navLinks) return;

    const isOpen =
      navLinks.classList.contains('is-open');

    if (isOpen) {
      closeNav();
    } else {
      openNav();
    }
  }

  if (navToggle && navLinks) {
    navToggle.addEventListener(
      'click',
      toggleNav
    );

    /* Close menu when any navigation link is clicked */

    navLinks.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        closeNav();
      });
    });

    /* Close menu when clicking outside it */

    document.addEventListener('click', (event) => {
      const clickedInsideMenu =
        navLinks.contains(event.target);

      const clickedToggle =
        navToggle.contains(event.target);

      if (
        navLinks.classList.contains('is-open') &&
        !clickedInsideMenu &&
        !clickedToggle
      ) {
        closeNav();
      }
    });

    /* Close menu with Escape key */

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        closeNav();
      }
    });

    /* Close mobile menu when screen becomes desktop size */

    window.addEventListener('resize', () => {
      if (window.innerWidth > 1180) {
        closeNav();
      }
    });
  }

  /* ==========================================================
     SCROLL REVEAL
     Room cards fade and slide in when entering the viewport.
     ========================================================== */

  const roomCards =
    document.querySelectorAll('.room-card');

  if (
    prefersReducedMotion ||
    !('IntersectionObserver' in window)
  ) {
    roomCards.forEach((card) => {
      card.classList.add('is-visible');
    });
  } else {
    const revealObserver =
      new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.classList.add(
                'is-visible'
              );

              revealObserver.unobserve(
                entry.target
              );
            }
          });
        },
        {
          threshold: 0.15,
          rootMargin: '0px 0px -40px 0px'
        }
      );

    roomCards.forEach((card, index) => {
      card.style.transitionDelay =
        `${Math.min(index, 4) * 70}ms`;

      revealObserver.observe(card);
    });
  }

  /* ==========================================================
     STAT COUNT-UP ANIMATION
     ========================================================== */

  const statEls =
    document.querySelectorAll('.stat__number');

  function formatNumber(number) {
    return number.toLocaleString('en-US');
  }

  function countUp(element) {
    const target =
      Number(
        element.getAttribute('data-count')
      ) || 0;

    if (target === 0) {
      element.textContent = '0';
      return;
    }

    if (prefersReducedMotion) {
      element.textContent =
        formatNumber(target);
      return;
    }

    const duration = 1200;
    const start = performance.now();

    function animate(now) {
      const progress = Math.min(
        (now - start) / duration,
        1
      );

      /* Ease-out cubic */

      const eased =
        1 - Math.pow(1 - progress, 3);

      element.textContent =
        formatNumber(
          Math.round(target * eased)
        );

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    }

    requestAnimationFrame(animate);
  }

  if (statEls.length) {
    if (!('IntersectionObserver' in window)) {
      statEls.forEach(countUp);
    } else {
      const statObserver =
        new IntersectionObserver(
          (entries, observer) => {
            entries.forEach((entry) => {
              if (entry.isIntersecting) {
                countUp(entry.target);

                observer.unobserve(
                  entry.target
                );
              }
            });
          },
          {
            threshold: 0.35
          }
        );

      statEls.forEach((element) => {
        statObserver.observe(element);
      });
    }
  }

  /* ==========================================================
     FEEDBACK + CONTACT FORMS
     Currently simulates form submission.
     Replace the timeout with a fetch() request when backend
     endpoints are available.
     ========================================================== */

  function wireSimpleForm(
    formId,
    submitId,
    noteId,
    successMessage
  ) {
    const form =
      document.getElementById(formId);

    const submitBtn =
      document.getElementById(submitId);

    const note =
      document.getElementById(noteId);

    if (
      !form ||
      !submitBtn ||
      !note
    ) {
      return;
    }

    form.addEventListener(
      'submit',
      (event) => {
        event.preventDefault();

        if (!form.checkValidity()) {
          form.reportValidity();
          return;
        }

        submitBtn.disabled = true;

        const label =
          submitBtn.querySelector(
            '.submit-label'
          );

        const originalLabel =
          label
            ? label.textContent
            : submitBtn.textContent;

        if (label) {
          label.textContent = 'Sending…';
        } else {
          submitBtn.textContent = 'Sending…';
        }

        note.textContent = '';

        /* Simulated submission */

        window.setTimeout(() => {
          if (label) {
            label.textContent =
              originalLabel;
          } else {
            submitBtn.textContent =
              originalLabel;
          }

          submitBtn.disabled = false;

          note.textContent =
            successMessage;

          form.reset();

          window.setTimeout(() => {
            note.textContent = '';
          }, 4000);

        }, 900);
      }
    );
  }

  wireSimpleForm(
    'feedbackForm',
    'feedbackSubmit',
    'feedbackNote',
    "Thanks — that's been sent to the team."
  );

  wireSimpleForm(
    'contactForm',
    'contactSubmit',
    'contactNote',
    "Message sent — we'll get back to you soon."
  );

})();