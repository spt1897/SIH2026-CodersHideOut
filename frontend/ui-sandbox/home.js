'use strict';

(function () {

  /* ==========================================================
     BASIC SETUP
  ========================================================== */

  const root = document.documentElement;

  const prefersReducedMotion =
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;


  /* ==========================================================
     THEME TOGGLE
  ========================================================== */

  const THEME_KEY = 'theme';

  const themeToggle =
    document.getElementById('themeToggle');


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
      // Ignore storage errors
    }

  }


  function applyTheme(theme) {

    root.setAttribute('data-theme', theme);

    const isLight = theme === 'light';

    if (themeToggle) {

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

  }


  applyTheme(
    root.getAttribute('data-theme') || 'dark'
  );


  if (themeToggle) {

    themeToggle.addEventListener(
      'click',
      function () {

        const current =
          root.getAttribute('data-theme');

        const next =
          current === 'light'
            ? 'dark'
            : 'light';

        applyTheme(next);

        storeTheme(next);

      }
    );

  }


  /* ==========================================================
     SYSTEM THEME CHANGE
  ========================================================== */

  if (window.matchMedia) {

    const mql =
      window.matchMedia(
        '(prefers-color-scheme: light)'
      );


    const onSystemThemeChange =
      function (event) {

        if (getStoredTheme()) {
          return;
        }

        applyTheme(
          event.matches
            ? 'light'
            : 'dark'
        );

      };


    if (mql.addEventListener) {

      mql.addEventListener(
        'change',
        onSystemThemeChange
      );

    } else if (mql.addListener) {

      mql.addListener(
        onSystemThemeChange
      );

    }

  }


  /* ==========================================================
     MOBILE NAVIGATION
  ========================================================== */

  const navToggle =
    document.getElementById('navToggle');

  const navLinks =
    document.getElementById('navLinks');


  if (navToggle && navLinks) {

    navToggle.addEventListener(
      'click',
      function () {

        const isOpen =
          navLinks.classList.toggle(
            'is-open'
          );

        navToggle.setAttribute(
          'aria-expanded',
          String(isOpen)
        );

        navToggle.setAttribute(
          'aria-label',
          isOpen
            ? 'Close menu'
            : 'Open menu'
        );

      }
    );


    navLinks
      .querySelectorAll('a')
      .forEach(function (link) {

        link.addEventListener(
          'click',
          function () {

            navLinks.classList.remove(
              'is-open'
            );

            navToggle.setAttribute(
              'aria-expanded',
              'false'
            );

            navToggle.setAttribute(
              'aria-label',
              'Open menu'
            );

          }
        );

      });

  }


  /* ==========================================================
     ROOM CARD SCROLL REVEAL
  ========================================================== */

  const roomCards =
    document.querySelectorAll(
      '.room-card'
    );


  if (
    prefersReducedMotion ||
    !('IntersectionObserver' in window)
  ) {

    roomCards.forEach(
      function (card) {
        card.classList.add(
          'is-visible'
        );
      }
    );

  } else {

    const revealObserver =
      new IntersectionObserver(
        function (entries) {

          entries.forEach(
            function (entry) {

              if (entry.isIntersecting) {

                entry.target.classList.add(
                  'is-visible'
                );

                revealObserver.unobserve(
                  entry.target
                );

              }

            }
          );

        },
        {
          threshold: 0.2,
          rootMargin: '0px 0px -40px 0px'
        }
      );


    roomCards.forEach(
      function (card, index) {

        card.style.transitionDelay =
          `${Math.min(index, 4) * 70}ms`;

        revealObserver.observe(card);

      }
    );

  }


  /* ==========================================================
     STAT COUNT UP
  ========================================================== */

  const statEls =
    document.querySelectorAll(
      '.stat__number'
    );


  function formatNumber(number) {

    return number.toLocaleString(
      'en-US'
    );

  }


  function countUp(element) {

    const target =
      Number(
        element.getAttribute(
          'data-count'
        )
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

    const start =
      performance.now();


    function tick(now) {

      const progress =
        Math.min(
          (now - start) / duration,
          1
        );


      const eased =
        1 -
        Math.pow(
          1 - progress,
          3
        );


      element.textContent =
        formatNumber(
          Math.round(
            target * eased
          )
        );


      if (progress < 1) {

        requestAnimationFrame(tick);

      }

    }


    requestAnimationFrame(tick);

  }


  if (statEls.length) {

    if (
      !('IntersectionObserver' in window)
    ) {

      statEls.forEach(countUp);

    } else {

      const statObserver =
        new IntersectionObserver(
          function (entries, observer) {

            entries.forEach(
              function (entry) {

                if (entry.isIntersecting) {

                  countUp(
                    entry.target
                  );

                  observer.unobserve(
                    entry.target
                  );

                }

              }
            );

          },
          {
            threshold: 0.5
          }
        );


      statEls.forEach(
        function (element) {

          statObserver.observe(
            element
          );

        }
      );

    }

  }


  /* ==========================================================
     PROFILE / LOGIN STATE
     
     The login page should save:
     
     localStorage.setItem('isLoggedIn', 'true');
     localStorage.setItem('userName', 'Shruti');
     localStorage.setItem('userEmail', 'shruti@example.com');
     localStorage.setItem('userProfile', 'profile-image-url');
     
  ========================================================== */

  const loggedOutActions =
    document.getElementById(
      'loggedOutActions'
    );

  const loggedInActions =
    document.getElementById(
      'loggedInActions'
    );


  const navProfileImage =
    document.getElementById(
      'navProfileImage'
    );

  const navUserName =
    document.getElementById(
      'navUserName'
    );

  const sidebarProfileImage =
    document.getElementById(
      'sidebarProfileImage'
    );

  const sidebarUserName =
    document.getElementById(
      'sidebarUserName'
    );

  const sidebarUserEmail =
    document.getElementById(
      'sidebarUserEmail'
    );


  function getUserData() {

    let loggedIn = false;
    let name = 'User';
    let email = 'user@example.com';
    let profile =
      'https://ui-avatars.com/api/?name=User&background=2563eb&color=fff';


    try {

      loggedIn =
        localStorage.getItem(
          'isLoggedIn'
        ) === 'true';


      name =
        localStorage.getItem(
          'userName'
        ) || 'User';


      email =
        localStorage.getItem(
          'userEmail'
        ) || 'user@example.com';


      profile =
        localStorage.getItem(
          'userProfile'
        ) ||
        `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=2563eb&color=fff`;

    } catch (error) {

      console.log(
        'Could not read user data.'
      );

    }


    return {
      loggedIn,
      name,
      email,
      profile
    };

  }


  function updateUserUI() {

    const user =
      getUserData();


    if (user.loggedIn) {

      if (loggedOutActions) {
        loggedOutActions.hidden = true;
      }

      if (loggedInActions) {
        loggedInActions.hidden = false;
      }


      if (navUserName) {
        navUserName.textContent =
          user.name;
      }


      if (navProfileImage) {
        navProfileImage.src =
          user.profile;
      }


      if (sidebarUserName) {
        sidebarUserName.textContent =
          user.name;
      }


      if (sidebarUserEmail) {
        sidebarUserEmail.textContent =
          user.email;
      }


      if (sidebarProfileImage) {
        sidebarProfileImage.src =
          user.profile;
      }

    } else {

      if (loggedOutActions) {
        loggedOutActions.hidden = false;
      }

      if (loggedInActions) {
        loggedInActions.hidden = true;
      }

    }

  }


  updateUserUI();


  /* ==========================================================
     PROFILE SIDEBAR
  ========================================================== */

  const profileTrigger =
    document.getElementById(
      'profileTrigger'
    );

  const profileSidebar =
    document.getElementById(
      'profileSidebar'
    );

  const profileClose =
    document.getElementById(
      'profileClose'
    );

  const profileOverlay =
    document.getElementById(
      'profileOverlay'
    );


  function openProfileSidebar() {

    if (!profileSidebar) {
      return;
    }


    profileSidebar.classList.add(
      'is-open'
    );


    profileOverlay.classList.add(
      'is-visible'
    );


    profileSidebar.setAttribute(
      'aria-hidden',
      'false'
    );


    profileOverlay.setAttribute(
      'aria-hidden',
      'false'
    );


    if (profileTrigger) {

      profileTrigger.setAttribute(
        'aria-expanded',
        'true'
      );

    }


    document.body.style.overflow =
      'hidden';

  }


  function closeProfileSidebar() {

    if (!profileSidebar) {
      return;
    }


    profileSidebar.classList.remove(
      'is-open'
    );


    profileOverlay.classList.remove(
      'is-visible'
    );


    profileSidebar.setAttribute(
      'aria-hidden',
      'true'
    );


    profileOverlay.setAttribute(
      'aria-hidden',
      'true'
    );


    if (profileTrigger) {

      profileTrigger.setAttribute(
        'aria-expanded',
        'false'
      );

    }


    document.body.style.overflow =
      '';

  }


  if (profileTrigger) {

    profileTrigger.addEventListener(
      'click',
      function () {

        const isOpen =
          profileSidebar.classList.contains(
            'is-open'
          );


        if (isOpen) {
          closeProfileSidebar();
        } else {
          openProfileSidebar();
        }

      }
    );

  }


  if (profileClose) {

    profileClose.addEventListener(
      'click',
      closeProfileSidebar
    );

  }


  if (profileOverlay) {

    profileOverlay.addEventListener(
      'click',
      closeProfileSidebar
    );

  }


  document.addEventListener(
    'keydown',
    function (event) {

      if (
        event.key === 'Escape'
      ) {

        closeProfileSidebar();

      }

    }
  );


  /* ==========================================================
     LOGOUT
  ========================================================== */

  const logoutBtn =
    document.getElementById(
      'logoutBtn'
    );


  if (logoutBtn) {

    logoutBtn.addEventListener(
      'click',
      function () {

        try {

          localStorage.removeItem(
            'isLoggedIn'
          );

          localStorage.removeItem(
            'userName'
          );

          localStorage.removeItem(
            'userEmail'
          );

          localStorage.removeItem(
            'userProfile'
          );

        } catch (error) {

          console.log(
            'Logout storage error.'
          );

        }


        closeProfileSidebar();

        updateUserUI();

        window.location.href =
          'home.html';

      }
    );

  }


  /* ==========================================================
     FEEDBACK FORM
  ========================================================== */

  const feedbackForm =
    document.getElementById(
      'feedbackForm'
    );

  const feedbackSuccess =
    document.getElementById(
      'feedbackSuccess'
    );


  if (feedbackForm) {

    feedbackForm.addEventListener(
      'submit',
      function (event) {

        event.preventDefault();


        const name =
          document.getElementById(
            'feedbackName'
          ).value.trim();

        const email =
          document.getElementById(
            'feedbackEmail'
          ).value.trim();

        const type =
          document.getElementById(
            'feedbackType'
          ).value;

        const message =
          document.getElementById(
            'feedbackMessage'
          ).value.trim();


        const feedback = {
          name,
          email,
          type,
          message,
          createdAt:
            new Date().toISOString()
        };


        try {

          const existing =
            JSON.parse(
              localStorage.getItem(
                'feedback'
              ) || '[]'
            );


          existing.push(
            feedback
          );


          localStorage.setItem(
            'feedback',
            JSON.stringify(existing)
          );

        } catch (error) {

          console.log(
            'Feedback could not be saved.'
          );

        }


        feedbackForm.reset();


        if (feedbackSuccess) {

          feedbackSuccess.hidden =
            false;


          setTimeout(
            function () {

              feedbackSuccess.hidden =
                true;

            },
            4000
          );

        }

      }
    );

  }


  /* ==========================================================
     AUTO-FILL FEEDBACK USER DETAILS
  ========================================================== */

  function fillFeedbackUser() {

    const user =
      getUserData();


    if (!user.loggedIn) {
      return;
    }


    const nameInput =
      document.getElementById(
        'feedbackName'
      );

    const emailInput =
      document.getElementById(
        'feedbackEmail'
      );


    if (
      nameInput &&
      !nameInput.value
    ) {

      nameInput.value =
        user.name;

    }


    if (
      emailInput &&
      !emailInput.value
    ) {

      emailInput.value =
        user.email;

    }

  }


  fillFeedbackUser();


  /* ==========================================================
     SMOOTH SCROLL
  ========================================================== */

  document
    .querySelectorAll(
      'a[href^="#"]'
    )
    .forEach(
      function (link) {

        link.addEventListener(
          'click',
          function (event) {

            const targetId =
              link.getAttribute(
                'href'
              );


            if (
              !targetId ||
              targetId === '#'
            ) {
              return;
            }


            const target =
              document.querySelector(
                targetId
              );


            if (!target) {
              return;
            }


            event.preventDefault();


            target.scrollIntoView({
              behavior:
                prefersReducedMotion
                  ? 'auto'
                  : 'smooth',
              block: 'start'
            });

          }
        );

      }
    );

})();