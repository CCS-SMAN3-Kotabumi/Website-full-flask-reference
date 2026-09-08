// Mobile menu toggle
  var hamburgerBtn = document.getElementById('hamburgerBtn');
  var mobileMenu = document.getElementById('mobileMenu');
  hamburgerBtn.addEventListener('click', function(){
    var open = mobileMenu.classList.toggle('open');
    hamburgerBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  // FAQ accordion
  document.querySelectorAll('.faq-q').forEach(function(btn){
    btn.addEventListener('click', function(){
      var item = btn.parentElement;
      var open = item.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });

  // Video placeholder keyboard support
  document.querySelectorAll('[role="button"]').forEach(function(el){
    el.addEventListener('keydown', function(e){
      if(e.key === 'Enter' || e.key === ' '){ e.preventDefault(); el.click(); }
    });
  });

  // Sticky nav shadow on scroll
  var nav = document.getElementById('siteNav');
  window.addEventListener('scroll', function(){
    nav.classList.toggle('scrolled', window.scrollY > 8);
  });

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Scroll reveal
  if('IntersectionObserver' in window && !reduceMotion){
    var revealObserver = new IntersectionObserver(function(entries){
      entries.forEach(function(entry){
        if(entry.isIntersecting){
          entry.target.classList.add('visible');
          revealObserver.unobserve(entry.target);
        }
      });
    }, {threshold:0.12});
    document.querySelectorAll('.reveal').forEach(function(el){ revealObserver.observe(el); });
  } else {
    document.querySelectorAll('.reveal').forEach(function(el){ el.classList.add('visible'); });
  }

  // Animated stat counters
  if('IntersectionObserver' in window){
    var countObserver = new IntersectionObserver(function(entries){
      entries.forEach(function(entry){
        if(entry.isIntersecting){
          var el = entry.target;
          var target = parseInt(el.getAttribute('data-count'), 10);
          if(reduceMotion){ el.textContent = target; countObserver.unobserve(el); return; }
          var start = 0;
          var duration = 900;
          var startTime = null;
          function step(ts){
            if(!startTime) startTime = ts;
            var progress = Math.min((ts - startTime) / duration, 1);
            el.textContent = Math.floor(progress * (target - start) + start);
            if(progress < 1){ requestAnimationFrame(step); } else { el.textContent = target; }
          }
          requestAnimationFrame(step);
          countObserver.unobserve(el);
        }
      });
    }, {threshold:0.5});
    document.querySelectorAll('.stat .num').forEach(function(el){ countObserver.observe(el); });
  }

  // Active nav link on scroll (scroll-spy)
  var sections = ['program','jadwal','pengurus','galeri','daftar'].map(function(id){ return document.getElementById(id); }).filter(Boolean);
  var navLinks = document.querySelectorAll('.navlinks a');
  if('IntersectionObserver' in window && sections.length){
    var spyObserver = new IntersectionObserver(function(entries){
      entries.forEach(function(entry){
        if(entry.isIntersecting){
          navLinks.forEach(function(link){
            link.classList.toggle('active', link.getAttribute('data-nav') === entry.target.id);
          });
        }
      });
    }, {rootMargin:'-40% 0px -50% 0px'});
    sections.forEach(function(sec){ spyObserver.observe(sec); });
  }