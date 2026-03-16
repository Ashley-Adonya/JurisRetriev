(() => {
  function showAdminFeedback(adminDocFeedback, msg, type = "error") {
    adminDocFeedback.textContent = msg;
    adminDocFeedback.classList.remove("hidden", "bg-red-50", "text-red-600", "bg-green-50", "text-green-600");
    if (type === "error") {
      adminDocFeedback.classList.add("bg-red-50", "text-red-600");
    } else {
      adminDocFeedback.classList.add("bg-green-50", "text-green-600");
    }
    setTimeout(() => adminDocFeedback.classList.add("hidden"), 4000);
  }

  async function initAdmin() {
    const adminContainer = document.getElementById("adminContainer");
    if (!adminContainer) return;

    if (!window.JRAuth) return;

    await window.JRAuth.refreshAuthState();
    window.JRAuth.updateNav();

    const state = window.JRAuth.getState();
    if (!state.isAuthenticated) {
      window.JRAuth.redirectToLogin("auth_required", "/admin");
      return;
    }

    if (!state.isAdmin) {
      window.JRAuth.redirectToLogin("admin_required", "/admin");
      return;
    }

    const adminUploadBtn = document.getElementById("adminUploadBtn");
    const adminDocInfo = document.getElementById("adminDocInfo");
    const adminDocText = document.getElementById("adminDocText");
    const adminDocFeedback = document.getElementById("adminDocFeedback");

    const errorDiv = document.getElementById("adminError");
    const errorMsg = document.getElementById("adminErrorMsg");

    async function loadStats() {
      try {
        const response = await fetch("/api/admin/stats");
        const data = await response.json();

        if (response.status === 401) {
          window.JRAuth.clearLocalAuthState();
          window.JRAuth.redirectToLogin("session_expired", "/admin");
          return;
        }

        if (response.status === 403) {
          window.JRAuth.redirectToLogin("admin_required", "/admin");
          return;
        }

        if (!data.ok) {
          if (errorDiv) errorDiv.classList.remove("hidden");
          if (errorMsg) errorMsg.innerText = data.message || "Erreur de chargement des statistiques.";
          return;
        }

        if (errorDiv) errorDiv.classList.add("hidden");

        const statTotalUsers = document.getElementById("statTotalUsers");
        const statTotalRequests = document.getElementById("statTotalRequests");
        if (statTotalUsers) statTotalUsers.innerText = data.stats.total_users;
        if (statTotalRequests) statTotalRequests.innerText = data.stats.total_chat_requests;

        const ul = document.getElementById("recentUsersList");
        if (!ul) return;

        ul.innerHTML = "";
        if (data.stats.recent_users.length === 0) {
          ul.innerHTML = '<li class="px-4 py-4 sm:px-6 text-sm text-gray-500 italic text-center">Aucun utilisateur récent.</li>';
          return;
        }

        data.stats.recent_users.forEach((u) => {
          const li = document.createElement("li");
          li.className = "px-4 py-4 sm:px-6 hover:bg-gray-50";
          li.innerHTML = `<div class="flex items-center justify-between"><p class="text-sm font-medium text-indigo-600 truncate">${u.email}</p><div class="ml-2 flex-shrink-0 flex"><p class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Inscrit le : ${u.created_at}</p></div></div>`;
          ul.appendChild(li);
        });
      } catch (err) {
        console.error("Admin stats error", err);
      }
    }

    if (adminUploadBtn && adminDocInfo && adminDocText && adminDocFeedback) {
      adminUploadBtn.addEventListener("click", async () => {
        if (!adminDocInfo.value || !adminDocText.value) {
          showAdminFeedback(adminDocFeedback, "Veuillez remplir les deux champs", "error");
          return;
        }

        const prevText = adminUploadBtn.innerText;
        adminUploadBtn.innerText = "Formatage & Indexation en cours...";
        adminUploadBtn.disabled = true;

        try {
          const response = await fetch("/api/rag/documents", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ docs: [{ doc_info: adminDocInfo.value, doc_text: adminDocText.value }] }),
          });
          const data = await response.json();

          if (response.status === 401) {
            window.JRAuth.clearLocalAuthState();
            window.JRAuth.redirectToLogin("session_expired", "/admin");
            return;
          }

          if (response.status === 403) {
            window.JRAuth.redirectToLogin("admin_required", "/admin");
            return;
          }

          if (!response.ok || !data.ok) {
            showAdminFeedback(adminDocFeedback, data.error || data.message || "Erreur non gérée");
            return;
          }

          showAdminFeedback(adminDocFeedback, "Le document a bien été scanné, formaté et indexé !", "success");
          adminDocInfo.value = "";
          adminDocText.value = "";
        } catch (_) {
          showAdminFeedback(adminDocFeedback, "Erreur réseau, vérifiez le backend.");
        } finally {
          adminUploadBtn.innerText = prevText;
          adminUploadBtn.disabled = false;
        }
      });
    }

    const refreshStatsBtn = document.getElementById("refreshStatsBtn");
    if (refreshStatsBtn) {
      refreshStatsBtn.addEventListener("click", loadStats);
    }

    await loadStats();
  }

  document.addEventListener("DOMContentLoaded", initAdmin);
})();
