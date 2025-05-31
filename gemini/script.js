document.addEventListener("DOMContentLoaded", () => {
  gsap.registerPlugin(ScrollTrigger);

  // Initialize Particles.js
  particlesJS("particles-js", {
    particles: {
      number: {
        value: 80, // 粒子數量
        density: {
          enable: true,
          value_area: 800,
        },
      },
      color: {
        value: "#ffffff", // 粒子顏色
      },
      shape: {
        type: "circle", // 粒子形狀
      },
      opacity: {
        value: 0.5,
        random: false,
        anim: {
          enable: false,
        },
      },
      size: {
        value: 3, // 粒子大小
        random: true,
      },
      line_linked: {
        enable: true,
        distance: 150,
        color: "#ffffff",
        opacity: 0.4,
        width: 1,
      },
      move: {
        enable: true,
        speed: 2, // 移動速度
        direction: "none",
        random: false,
        straight: false,
        out_mode: "out",
        bounce: false,
      },
    },
    interactivity: {
      detect_on: "canvas",
      events: {
        onhover: {
          enable: true,
          mode: "repulse", // 滑鼠懸停效果
        },
        onclick: {
          enable: true,
          mode: "push", // 滑鼠點擊效果
        },
        resize: true,
      },
      modes: {
        repulse: {
          distance: 100,
          duration: 0.4,
        },
        push: {
          particles_nb: 4,
        },
      },
    },
    retina_detect: true,
  });

  // Hero Section Animations
  const heroTl = gsap.timeline({ defaults: { ease: "power3.out" } });
  heroTl
    .to(".hero-content", { opacity: 1, y: 0, duration: 0.8, delay: 0.2 })
    .to(
      ".main-title span",
      {
        opacity: 1,
        y: 0,
        scale: 1,
        stagger: 0.1,
        duration: 0.6,
      },
      "-=0.5"
    )
    .to(".subtitle", { opacity: 1, y: 0, duration: 0.6 }, "-=0.4")
    .to(
      ".cta-buttons .btn",
      { opacity: 1, y: 0, stagger: 0.2, duration: 0.5 },
      "-=0.3"
    )
    .to(".scroll-indicator", { opacity: 1, duration: 0.5 }, "-=0.2");

  // Common function for section title animation
  function animateSectionTitle(selector) {
    gsap.to(selector, {
      opacity: 1,
      y: 0,
      duration: 0.8,
      ease: "power3.out",
      scrollTrigger: {
        trigger: selector,
        start: "top 85%", // 元素頂部到達視窗85%位置時觸發
        toggleActions: "play none none none", // 觸發一次
      },
    });
  }

  animateSectionTitle(".section-data-glance .section-title");
  animateSectionTitle(".section-flow .section-title");
  animateSectionTitle(".section-final-cta .section-title");

  // Data Glance Section - Cards Animation
  gsap.utils.toArray(".data-card").forEach((card, index) => {
    gsap.to(card, {
      opacity: 1,
      y: 0,
      scale: 1,
      duration: 0.7,
      delay: index * 0.15, // Stagger
      ease: "power2.out",
      scrollTrigger: {
        trigger: ".data-visuals",
        start: "top 75%",
        toggleActions: "play none none none",
      },
    });
  });

  // Data Glance - Number Counting Animation
  gsap.utils.toArray(".amount[data-target]").forEach((amountEl) => {
    gsap.to(amountEl, {
      innerText: parseFloat(amountEl.dataset.target),
      duration: 2,
      ease: "power1.inOut",
      snap: { innerText: 1 }, // 捕捉到整數
      formatter: (value) => `NT$ ${Math.round(value).toLocaleString()}`, // 格式化輸出
      scrollTrigger: {
        trigger: amountEl,
        start: "top 85%",
        toggleActions: "play none none none",
      },
    });
  });

  // Data Glance - Mini Chart Bar Animation
  gsap.utils.toArray(".mini-chart .bar").forEach((bar) => {
    gsap.to(bar, {
      height: bar.dataset.height,
      opacity: 1,
      duration: 1,
      ease: "elastic.out(1, 0.75)",
      stagger: 0.1,
      scrollTrigger: {
        trigger: ".mini-chart",
        start: "top 90%",
        toggleActions: "play none none none",
      },
    });
  });

  // Flow Section - Steps Animation
  const flowSteps = gsap.utils.toArray(".flow-step, .flow-arrow");
  gsap.to(flowSteps, {
    opacity: 1,
    scale: 1,
    duration: 0.6,
    stagger: 0.2,
    ease: "back.out(1.7)",
    scrollTrigger: {
      trigger: ".flow-diagram",
      start: "top 70%",
      toggleActions: "play none none none",
    },
  });

  // Final CTA Section Animation
  const finalCtaTl = gsap.timeline({
    scrollTrigger: {
      trigger: ".section-final-cta",
      start: "top 70%",
      toggleActions: "play none none none",
    },
  });
  finalCtaTl
    .to(".section-final-cta p", {
      opacity: 1,
      y: 0,
      duration: 0.7,
      ease: "power2.out",
    })
    .to(
      ".section-final-cta .btn-large",
      { opacity: 1, scale: 1, duration: 0.7, ease: "elastic.out(1, 0.75)" },
      "-=0.4"
    );
  // 功能區塊標題動畫
  gsap.to(".section-title", {
    scrollTrigger: {
      trigger: ".section-title",
      start: "top 80%",
      end: "bottom 20%",
      toggleActions: "play none none reverse",
    },
    opacity: 1,
    y: 0,
    duration: 1,
    ease: "power3.out",
  });

  // 功能卡片動畫
  gsap.to(".feature-card", {
    scrollTrigger: {
      trigger: ".features-grid",
      start: "top 80%",
      end: "bottom 20%",
      toggleActions: "play none none reverse",
    },
    opacity: 1,
    y: 0,
    duration: 0.8,
    ease: "power3.out",
    stagger: 0.2,
  });

  // 統計數據動畫
  const statItems = gsap.utils.toArray(".stat-item");

  statItems.forEach((item, index) => {
    gsap.to(item, {
      scrollTrigger: {
        trigger: ".stats-section",
        start: "top 60%",
        end: "bottom 40%",
        toggleActions: "play none none reverse",
      },
      opacity: 1,
      y: 0,
      duration: 0.8,
      ease: "power3.out",
      delay: index * 0.1,
    });
  });

  // 數字計數動畫
  ScrollTrigger.create({
    trigger: ".stats-section",
    start: "top 60%",
    onEnter: () => {
      // 用戶數量
      gsap.to(
        { value: 0 },
        {
          value: 50000,
          duration: 2,
          ease: "power2.out",
          onUpdate: function () {
            document.getElementById("users-count").textContent =
              Math.floor(this.targets()[0].value).toLocaleString() + "+";
          },
        }
      );

      // 交易筆數
      gsap.to(
        { value: 0 },
        {
          value: 1200000,
          duration: 2.2,
          ease: "power2.out",
          onUpdate: function () {
            document.getElementById("transactions-count").textContent =
              Math.floor(this.targets()[0].value).toLocaleString() + "+";
          },
        }
      );

      // 節省金額
      gsap.to(
        { value: 0 },
        {
          value: 5000000,
          duration: 2.4,
          ease: "power2.out",
          onUpdate: function () {
            document.getElementById("savings-count").textContent =
              "NT$" + Math.floor(this.targets()[0].value).toLocaleString();
          },
        }
      );

      // 滿意度
      gsap.to(
        { value: 0 },
        {
          value: 98,
          duration: 2.6,
          ease: "power2.out",
          onUpdate: function () {
            document.getElementById("satisfaction-count").textContent =
              Math.floor(this.targets()[0].value) + "%";
          },
        }
      );
    },
  });
});
