(() => {
  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function markdownToSafeHtml(markdownText) {
    const raw = String(markdownText ?? "");

    if (window.marked && typeof window.marked.parse === "function") {
      const rendered = window.marked.parse(raw, { gfm: true, breaks: true });
      if (window.DOMPurify && typeof window.DOMPurify.sanitize === "function") {
        return window.DOMPurify.sanitize(rendered);
      }
      return rendered;
    }

    return escapeHtml(raw).replace(/\n/g, "<br>");
  }

  function appendMessage(chatBox, sender, htmlContent, type, isBuilding = false, createdAt = null) {
    const wrapper = document.createElement("div");
    const isUser = type === "user";
    wrapper.className = `chat-msg flex flex-col ${isUser ? "items-end" : "items-start"} mb-4`;

    const bubble = document.createElement("div");
    bubble.className = `max-w-3xl px-5 py-4 rounded-xl shadow-sm whitespace-pre-line ${isUser ? "bg-slate-900 text-white" : "bg-white text-gray-800 border border-gray-200"}`;

    const label = document.createElement("div");
    label.className = `text-xs font-bold mb-2 uppercase tracking-wide ${isUser ? "text-gray-400" : "text-blue-600"}`;
    label.innerText = sender;

    if (createdAt) {
      const ts = document.createElement("span");
      ts.className = "ml-2 text-[10px] font-normal text-gray-400 normal-case";
      try {
        const d = new Date(createdAt);
        ts.innerText = d.toLocaleString();
      } catch (_) {
        ts.innerText = createdAt;
      }
      label.appendChild(ts);
    }

    const content = document.createElement("div");
    content.className = "text-sm leading-relaxed";
    content.innerHTML = htmlContent;
    if (isBuilding) content.classList.add("animate-pulse");

    bubble.appendChild(label);
    bubble.appendChild(content);
    wrapper.appendChild(bubble);
    chatBox.appendChild(wrapper);
    chatBox.scrollTop = chatBox.scrollHeight;

    return content;
  }

  function clearTimeline(chatBox) {
    chatBox.querySelectorAll(".chat-msg").forEach((node) => node.remove());
  }

  function createConversationId() {
    return `conv-${Date.now()}`;
  }

  function formatDateShort(iso) {
    if (!iso) return "";
    try {
      return new Date(iso).toLocaleString();
    } catch (_) {
      return "";
    }
  }

  async function initChat() {
    const chatForm = document.getElementById("chatForm");
    if (!chatForm) return;

    if (!window.JRAuth) return;

    await window.JRAuth.refreshAuthState();
    window.JRAuth.updateNav();

    const authState = window.JRAuth.getState();
    if (!authState.isAuthenticated) {
      window.JRAuth.redirectToLogin("auth_required", "/chat");
      return;
    }

    const queryInput = document.getElementById("queryInput");
    const queryMode = document.getElementById("queryMode");
    const chatBox = document.getElementById("chatBox");
    const tempDocInfo = document.getElementById("tempDocInfo");
    const tempDocText = document.getElementById("tempDocText");
    const quotaModal = document.getElementById("quotaModal");
    const conversationList = document.getElementById("conversationList");
    const newConversationBtn = document.getElementById("newConversationBtn");

    let conversationId = localStorage.getItem("conversationId") || null;
    let conversations = [];

    const closeQuotaBtn = document.getElementById("closeQuotaModalBtn");
    if (closeQuotaBtn) {
      closeQuotaBtn.addEventListener("click", () => quotaModal.classList.add("hidden"));
    }

    function renderConversationList() {
      if (!conversationList) return;

      if (!conversations.length) {
        conversationList.innerHTML = '<p class="text-xs text-gray-500 italic">Aucune conversation enregistrée.</p>';
        return;
      }

      conversationList.innerHTML = "";
      conversations.forEach((conv) => {
        const isActive = conv.conversation_id === conversationId;
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = `w-full text-left p-2 rounded border transition ${isActive ? "border-blue-300 bg-blue-50" : "border-gray-200 hover:bg-gray-50"}`;
        btn.innerHTML = `
          <div class="text-xs font-semibold text-slate-900 truncate">${escapeHtml(conv.title || "Conversation")}</div>
          <div class="text-[11px] text-gray-500 mt-1">${escapeHtml(formatDateShort(conv.last_created_at))}</div>
        `;
        btn.addEventListener("click", async () => {
          conversationId = conv.conversation_id;
          localStorage.setItem("conversationId", conversationId);
          renderConversationList();
          await loadHistory();
        });
        conversationList.appendChild(btn);
      });
    }

    async function loadConversations() {
      try {
        const res = await fetch("/api/rag/conversations?limit=40");
        const data = await res.json();
        if (!res.ok || !data.ok) {
          conversations = [];
          renderConversationList();
          return;
        }

        conversations = data.items || [];
        if (!conversationId && conversations.length > 0) {
          conversationId = conversations[0].conversation_id;
          localStorage.setItem("conversationId", conversationId);
        }
        renderConversationList();
      } catch (_) {
        conversations = [];
        renderConversationList();
      }
    }

    async function loadHistory() {
      clearTimeline(chatBox);
      if (!conversationId) {
        return;
      }

      try {
        const params = new URLSearchParams({ conversation_id: conversationId, limit: "100" });
        const res = await fetch(`/api/rag/history?${params.toString()}`);
        const data = await res.json();
        if (!res.ok || !data.ok) return;

        if (data.items && data.items.length > 0) {
          data.items.slice().reverse().forEach((item) => {
            appendMessage(chatBox, "Vous", item.query, "user", false, item.created_at);

            if (!item.answer) return;

            let displayHtml = markdownToSafeHtml(item.answer || "");
            if (item.rewritten_query && item.rewritten_query !== item.query) {
              displayHtml = `<div class="text-xs text-gray-400 bg-gray-50 p-2 rounded mb-3 border border-gray-100"><i>Question perçue: ${escapeHtml(item.rewritten_query)}</i></div>` + displayHtml;
            }

            if (item.temp_docs && item.temp_docs.length > 0) {
              const docsLabel = item.temp_docs.map((d) => escapeHtml(d.doc_info || "Document utilisateur")).join(", ");
              displayHtml += `<div class="mt-3 text-[11px] text-gray-500 italic">Contexte fourni : ${docsLabel}</div>`;
            }

            appendMessage(chatBox, "Assistant IA ⚖️", displayHtml, "ai", false, item.created_at);
          });
        }
      } catch (err) {
        console.error("history_load_error", err);
      }
    }

    if (newConversationBtn) {
      newConversationBtn.addEventListener("click", async () => {
        conversationId = createConversationId();
        localStorage.setItem("conversationId", conversationId);
        clearTimeline(chatBox);
        renderConversationList();
      });
    }

    await loadConversations();
    await loadHistory();

    chatForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const query = queryInput.value;
      if (!query) return;

      if (!conversationId) {
        conversationId = `conv-${Date.now()}`;
        localStorage.setItem("conversationId", conversationId);
      }

      appendMessage(chatBox, "Vous", query, "user");
      queryInput.value = "";

      const msgUi = appendMessage(chatBox, "Assistant IA ⚖️", "Analyse documentaire en cours...", "ai", true);

      const temp_docs = [];
      if (tempDocText.value.trim() !== "") {
        temp_docs.push({
          doc_info: tempDocInfo.value.trim() || "Document Temporaire (Utilisateur)",
          doc_text: tempDocText.value.trim(),
        });
      }

      try {
        const res = await fetch("/api/rag/query", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            query,
            mode: queryMode.value,
            topk: 3,
            temp_docs,
            conversation_id: conversationId,
          }),
        });

        const data = await res.json();
        msgUi.classList.remove("animate-pulse");

        if (res.status === 429) {
          quotaModal.classList.remove("hidden");
          msgUi.innerHTML = "<span class='text-red-600 font-bold'>Erreur: Quota d'utilisation dépassé.</span>";
          return;
        }

        if (res.status === 401) {
          window.JRAuth.clearLocalAuthState();
          window.JRAuth.redirectToLogin("session_expired", "/chat");
          return;
        }

        if (!res.ok || !data.ok) {
          msgUi.innerText = "Erreur: " + (data.error || data.message || "Traitement impossible.");
          msgUi.classList.add("text-red-500");
          return;
        }

        let displayHtml = markdownToSafeHtml(data.answer || "");

        if (data.retrieved && data.retrieved.length > 0) {
          displayHtml += `<div class="mt-4 pt-4 border-t border-gray-100">`;
          displayHtml += `<div class="text-xs font-bold text-gray-500 mb-2">SOURCES UTILISÉES :</div>`;

          data.retrieved.forEach((r) => {
            let sourceName = "Source Inconnue";
            if (r.doc && r.doc.doc_info) sourceName = r.doc.doc_info;
            displayHtml += `<span class="inline-block bg-blue-50 text-blue-800 text-xs px-2 py-1 rounded mr-2 mb-2 border border-blue-100">📄 ${escapeHtml(sourceName)}</span>`;
          });

          displayHtml += `</div>`;
        }

        if (data.rewritten_query && data.rewritten_query !== query) {
          displayHtml = `<div class="text-xs text-gray-400 bg-gray-50 p-2 rounded mb-3 border border-gray-100"><i>Question perçue: ${escapeHtml(data.rewritten_query)}</i></div>` + displayHtml;
        }

        msgUi.innerHTML = displayHtml;
        await loadConversations();
        renderConversationList();
      } catch (_) {
        msgUi.innerText = "Erreur de connexion à l'API IA.";
        msgUi.classList.add("text-red-500", "font-bold");
      }
    });
  }

  document.addEventListener("DOMContentLoaded", initChat);
})();
