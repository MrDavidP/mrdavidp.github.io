/**
 * hoodtip-nav.js
 * Swaps nav CTA to "+ Add a tip" when signed in.
 * Safe to include on any page — no duplicate UI elements.
 */
(function() {
  var SB_URL = 'https://lgyjsqwnicbbcqsfpuop.supabase.co';
  var SB_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxneWpzcXduaWNiYmNxc2ZwdW9wIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgyNDUzMTEsImV4cCI6MjA5MzgyMTMxMX0.lUsEAtYNG5OaIGfbdpedKEImjPw_eIzt69oIjrmHhvQ';

  // Prevent running twice
  if (window._htNavRan) return;
  window._htNavRan = true;

  if (!window.supabase) return;
  var sb = window.supabase.createClient(SB_URL, SB_KEY);

  sb.auth.getSession().then(function(ref) {
    var session = ref.data.session;
    if (!session || !session.user) return;

    // Swap all nav CTAs
    document.querySelectorAll('a.nav-cta, a.cta').forEach(function(a) {
      a.href = 'add-tips.html';
      a.textContent = '+ Add a tip';
    });

    // Update profile link if present
    sb.from('contributors').select('handle').eq('user_id', session.user.id).single().then(function(r) {
      if (!r.data) return;
      var handle = r.data.handle;
      document.querySelectorAll('a[href*="profile-dave"], a.nav-link').forEach(function(a) {
        if (a.textContent.trim() === 'Dave' || a.textContent.trim() === 'My profile' || a.href.indexOf('profile-dave') > -1) {
          a.href = 'profile.html?handle=' + handle;
          a.textContent = 'My profile';
        }
      });
    });
  });
})();
