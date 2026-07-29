// =============================================================================
// Archive — RAG chat frontend
// Talks to the existing FastAPI backend exactly as specified. No endpoint,
// request, or response shape is altered here.
// =============================================================================

(() => {
  "use strict";

  // ---- marked / DOMPurify config -------------------------------------------
  marked.setOptions({ breaks: true, gfm: true });

  function renderMarkdown(raw) {
    const html = marked.parse(raw || "");
    return DOMPurify.sanitize(html);
  }

  // ---- state ------------------------------------------------------------
  const state = {
    conversationId: null,
    topK: 5,
    summarize: false,
    isSending: false,
    conversations: [], // {id, title, created_at}
  };

  // ---- element refs -------------------------------------------------------
  const el = {
    app: document.querySelector(".app"),
    sidebar: document.getElementById("sidebar"),
    conversationList: document.getElementById("conversationList"),
    emptyConversations: document.getElementById("emptyConversations"),
    newChatBtn: document.getElementById("newChatBtn"),
    collapseSidebarBtn: document.getElementById("collapseSidebarBtn"),
    openSidebarBtn: document.getElementById("openSidebarBtn"),

    conversationTitle: document.getElementById("conversationTitle"),
    uploadNavBtn: document.getElementById("uploadNavBtn"),

    chatScroll: document.getElementById("chatScroll"),
    welcomeScreen: document.getElementById("welcomeScreen"),
    messages: document.getElementById("messages"),
    typingRow: document.getElementById("typingRow"),

    messageInput: document.getElementById("messageInput"),
    sendBtn: document.getElementById("sendBtn"),

    settingsPanel: document.getElementById("settingsPanel"),
    settingsToggleBtn: document.getElementById("settingsToggleBtn"),
    closeSettingsBtn: document.getElementById("closeSettingsBtn"),

    topKSlider: document.getElementById("topKSlider"),
    topKValue: document.getElementById("topKValue"),
    summarizeToggle: document.getElementById("summarizeToggle"),

    dropzone: document.getElementById("dropzone"),
    dropzoneInner: document.getElementById("dropzoneInner"),
    fileInput: document.getElementById("fileInput"),
    uploadProgress: document.getElementById("uploadProgress"),
    uploadProgressBar: document.getElementById("uploadProgressBar"),
    uploadStatus: document.getElementById("uploadStatus"),

    docList: document.getElementById("docList"),
    docEmpty: document.getElementById("docEmpty"),
    refreshDocsBtn: document.getElementById("refreshDocsBtn"),

    scrim: document.getElementById("scrim"),
  };

  // ---------------------------------------------------------------------
  // Sidebar / settings panel open-close (mobile + desktop collapse)
  // ---------------------------------------------------------------------
  function openMobilePanel(panel) {
    el.app.classList.add(panel === "sidebar" ? "sidebar-open" : "settings-open");
  }
  function closeMobilePanels() {
    el.app.classList.remove("sidebar-open", "settings-open");
  }

  el.openSidebarBtn.addEventListener("click", () => {
    if (window.innerWidth <= 980) { openMobilePanel("sidebar"); }
    else { el.app.classList.remove("sidebar-collapsed"); }
  });
  el.scrim.addEventListener("click", closeMobilePanels);

  el.collapseSidebarBtn.addEventListener("click", () => {
    if (window.innerWidth <= 980) { closeMobilePanels(); return; }
    el.app.classList.toggle("sidebar-collapsed");
  });

  el.settingsToggleBtn.addEventListener("click", () => {
    if (window.innerWidth <= 980) { openMobilePanel("settings"); return; }
    el.app.classList.remove("settings-collapsed");
  });
  el.closeSettingsBtn.addEventListener("click", () => {
    if (window.innerWidth <= 980) { closeMobilePanels(); return; }
    el.app.classList.add("settings-collapsed");
  });

  // ---------------------------------------------------------------------
  // Conversations — load / render / select / delete
  // ---------------------------------------------------------------------
  async function fetchConversations() {
    try {
      const res = await fetch("/history/conversations");
      if (!res.ok) throw new Error("Failed to load conversations");
      state.conversations = await res.json();
      renderConversationList();
    } catch (err) {
      console.error(err);
    }
  }

  function renderConversationList() {
    el.conversationList.querySelectorAll(".conversation-item").forEach((n) => n.remove());
    el.emptyConversations.hidden = state.conversations.length > 0;

    state.conversations.forEach((conv) => {
      const item = document.createElement("div");
      item.className = "conversation-item" + (conv.id === state.conversationId ? " active" : "");
      item.dataset.id = conv.id;

      const title = document.createElement("span");
      title.className = "conv-title";
      title.textContent = conv.title || "Untitled conversation";

      const delBtn = document.createElement("button");
      delBtn.className = "conv-delete-btn";
      delBtn.title = "Delete conversation";
      delBtn.innerHTML = '<svg width="13" height="13" viewBox="0 0 16 16" fill="none"><path d="M3 5h10M6.5 5V3.5A1 1 0 017.5 2.5h1A1 1 0 019.5 3.5V5M7 8v4M9 8v4M4 5l.6 8a1 1 0 001 .9h4.8a1 1 0 001-.9L12 5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>';
      delBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        deleteConversation(conv.id);
      });

      item.appendChild(title);
      item.appendChild(delBtn);
      item.addEventListener("click", () => loadConversation(conv.id));
      el.conversationList.appendChild(item);
    });
  }

  async function loadConversation(id) {
    if (state.isSending) return;
    try {
      const res = await fetch(`/history/conversations/${id}`);
      if (!res.ok) throw new Error("Failed to load conversation");
      const data = await res.json();

      state.conversationId = id;
      el.conversationTitle.textContent = (data.conversation && data.conversation.title) || "Conversation";
      renderConversationList();
      closeMobilePanels();

      el.messages.innerHTML = "";
      (data.messages || []).forEach((m) => {
        if (m.role === "user") {
          appendUserMessage(m.content);
        } else {
          appendAssistantMessage(m.content, []);
        }
      });
      toggleWelcome();
      scrollToBottom();
    } catch (err) {
      console.error(err);
    }
  }

  async function deleteConversation(id) {
    try {
      const res = await fetch(`/history/conversations/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Failed to delete conversation");
      state.conversations = state.conversations.filter((c) => c.id !== id);
      if (state.conversationId === id) {
        startNewConversation();
      }
      renderConversationList();
    } catch (err) {
      console.error(err);
    }
  }

  function startNewConversation() {
    state.conversationId = null;
    el.conversationTitle.textContent = "New conversation";
    el.messages.innerHTML = "";
    toggleWelcome();
    renderConversationList();
    closeMobilePanels();
    el.messageInput.focus();
  }

  el.newChatBtn.addEventListener("click", startNewConversation);

  function toggleWelcome() {
    el.welcomeScreen.hidden = el.messages.children.length > 0;
  }

  // ---------------------------------------------------------------------
  // Message rendering
  // ---------------------------------------------------------------------
  function scrollToBottom() {
    requestAnimationFrame(() => {
      el.chatScroll.scrollTop = el.chatScroll.scrollHeight;
    });
  }

  function appendUserMessage(text) {
    const row = document.createElement("div");
    row.className = "msg-row user";
    row.innerHTML = `
      <div class="msg-avatar user-avatar">YOU</div>
      <div class="msg-col">
        <div class="bubble"></div>
      </div>
    `;
    row.querySelector(".bubble").textContent = text;
    el.messages.appendChild(row);
    toggleWelcome();
    scrollToBottom();
    return row;
  }

  function appendAssistantMessage(answer, sources) {
    const row = document.createElement("div");
    row.className = "msg-row assistant";

    const col = document.createElement("div");
    col.className = "msg-col";

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.innerHTML = renderMarkdown(answer);

    const actions = document.createElement("div");
    actions.className = "msg-actions";
    actions.innerHTML = `
      <button class="msg-action-btn copy-btn" title="Copy response">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><rect x="5.5" y="5.5" width="8" height="8" rx="1.5" stroke="currentColor" stroke-width="1.3"/><path d="M3.5 10.5V4a1.5 1.5 0 011.5-1.5h6.5" stroke="currentColor" stroke-width="1.3"/></svg>
      </button>
    `;
    const copyBtn = actions.querySelector(".copy-btn");
    copyBtn.addEventListener("click", () => {
      navigator.clipboard.writeText(answer).then(() => {
        copyBtn.classList.add("copied");
        setTimeout(() => copyBtn.classList.remove("copied"), 1200);
      });
    });

    col.appendChild(bubble);
    col.appendChild(actions);

    if (Array.isArray(sources) && sources.length > 0) {
      col.appendChild(buildSourcesBlock(sources));
    }

    row.innerHTML = `<div class="msg-avatar assistant-avatar">◆</div>`;
    row.appendChild(col);

    el.messages.appendChild(row);
    toggleWelcome();
    scrollToBottom();
    return row;
  }

  function buildSourcesBlock(sources) {
    const block = document.createElement("div");
    block.className = "sources-block";

    const toggle = document.createElement("button");
    toggle.className = "sources-toggle";
    toggle.innerHTML = `
      <span class="chev"><svg width="10" height="10" viewBox="0 0 16 16" fill="none"><path d="M3 6l5 5 5-5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
      <span>Sources · ${sources.length}</span>
    `;

    const drawer = document.createElement("div");
    drawer.className = "sources-drawer";

    const cards = document.createElement("div");
    cards.className = "sources-cards";

    sources.forEach((s) => {
      const card = document.createElement("div");
      card.className = "source-card";
      const pageLabel = (s.page === 0 || s.page) ? `p.${s.page}` : "";
      const distLabel = (typeof s.distance === "number") ? `distance ${s.distance.toFixed(2)}` : "";
      card.innerHTML = `
        <div class="source-card-bar"></div>
        <div class="source-card-body">
          <div class="source-card-top">
            <span class="source-card-name">${escapeHtml(s.source || "Unknown source")}</span>
            <span class="source-card-meta">${escapeHtml(pageLabel)}</span>
          </div>
          ${s.preview ? `<div class="source-card-preview">${escapeHtml(s.preview)}</div>` : ""}
          ${distLabel ? `<div class="source-card-dist">${escapeHtml(distLabel)}</div>` : ""}
        </div>
      `;
      cards.appendChild(card);
    });

    drawer.appendChild(cards);
    toggle.addEventListener("click", () => {
      toggle.classList.toggle("open");
      drawer.classList.toggle("open");
    });

    block.appendChild(toggle);
    block.appendChild(drawer);
    return block;
  }

  function escapeHtml(str) {
    const d = document.createElement("div");
    d.textContent = str;
    return d.innerHTML;
  }

  // ---------------------------------------------------------------------
  // Sending a message
  // ---------------------------------------------------------------------
  function setSending(isSending) {
    state.isSending = isSending;
    el.sendBtn.disabled = isSending;
    el.sendBtn.innerHTML = isSending
      ? '<svg class="spinner" width="15" height="15" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.6" stroke-dasharray="28" stroke-dashoffset="10" stroke-linecap="round"/></svg>'
      : '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 13V3M8 3L3.5 7.5M8 3l4.5 4.5" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    el.typingRow.hidden = !isSending;
    if (isSending) scrollToBottom();
  }

  async function sendMessage() {
    const question = el.messageInput.value.trim();
    if (!question || state.isSending) return;

    appendUserMessage(question);
    el.messageInput.value = "";
    autosizeInput();
    setSending(true);

    const payload = {
      question,
      conversation_id: state.conversationId,
      top_k: state.topK,
      stream: false,
      summarize: state.summarize,
    };

    try {
      const res = await fetch("/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(`Request failed (${res.status})`);
      const data = await res.json();

      state.conversationId = data.conversation_id;
      appendAssistantMessage(data.answer, data.sources || []);

      if (el.conversationTitle.textContent === "New conversation") {
        el.conversationTitle.textContent = question.length > 48 ? question.slice(0, 48) + "…" : question;
      }
      await fetchConversations();
    } catch (err) {
      console.error(err);
      appendAssistantMessage(
        "Something went wrong reaching the server. Please try again.",
        []
      );
    } finally {
      setSending(false);
    }
  }

  el.sendBtn.addEventListener("click", sendMessage);
  el.messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  function autosizeInput() {
    el.messageInput.style.height = "auto";
    el.messageInput.style.height = Math.min(el.messageInput.scrollHeight, 200) + "px";
  }
  el.messageInput.addEventListener("input", autosizeInput);

  // ---------------------------------------------------------------------
  // Settings — top-k slider, summarize toggle
  // ---------------------------------------------------------------------
  el.topKSlider.addEventListener("input", () => {
    state.topK = parseInt(el.topKSlider.value, 10);
    el.topKValue.textContent = state.topK;
  });
  el.summarizeToggle.addEventListener("change", () => {
    state.summarize = el.summarizeToggle.checked;
  });

  // ---------------------------------------------------------------------
  // Upload — drag & drop + progress
  // ---------------------------------------------------------------------
  function openSettingsForUpload() {
    if (window.innerWidth <= 980) { openMobilePanel("settings"); }
    else { el.app.classList.remove("settings-collapsed"); }
  }
  el.uploadNavBtn.addEventListener("click", openSettingsForUpload);

  el.dropzone.addEventListener("click", () => el.fileInput.click());
  el.dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    el.dropzone.classList.add("drag-over");
  });
  el.dropzone.addEventListener("dragleave", () => el.dropzone.classList.remove("drag-over"));
  el.dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    el.dropzone.classList.remove("drag-over");
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      uploadFile(e.dataTransfer.files[0]);
    }
  });
  el.fileInput.addEventListener("change", () => {
    if (el.fileInput.files && el.fileInput.files[0]) {
      uploadFile(el.fileInput.files[0]);
    }
  });

  function uploadFile(file) {
    if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
      setUploadStatus("Only PDF files are supported.", "error");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    el.uploadProgress.hidden = false;
    el.uploadProgressBar.style.width = "0%";
    setUploadStatus(`Uploading ${file.name}…`, "");

    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/upload");

    xhr.upload.addEventListener("progress", (e) => {
      if (e.lengthComputable) {
        const pct = Math.round((e.loaded / e.total) * 100);
        el.uploadProgressBar.style.width = pct + "%";
      }
    });

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        el.uploadProgressBar.style.width = "100%";
        setUploadStatus(`${file.name} indexed successfully.`, "success");
        fetchDocuments();
      } else {
        setUploadStatus(`Upload failed (${xhr.status}).`, "error");
      }
      setTimeout(() => { el.uploadProgress.hidden = true; }, 900);
    };

    xhr.onerror = () => {
      setUploadStatus("Upload failed — network error.", "error");
      el.uploadProgress.hidden = true;
    };

    xhr.send(formData);
  }

  function setUploadStatus(text, kind) {
    el.uploadStatus.textContent = text;
    el.uploadStatus.className = "upload-status" + (kind ? " " + kind : "");
  }

  // ---------------------------------------------------------------------
  // Indexed documents — list + delete
  //
  // NOTE: the original backend spec only defines POST /upload, with no
  // route to list or remove indexed files. This section calls two small
  // additive endpoints — GET /documents and DELETE /documents/{filename} —
  // that would need to be added server-side. Nothing here touches /query,
  // /upload, or /history. If those routes aren't present yet, the panel
  // degrades to a note instead of breaking.
  // ---------------------------------------------------------------------
  // ---------------------------------------------------------------------
  // Indexed documents — list + delete
  // Backed by GET /documents -> [{id, filename, chunks}] and
  // DELETE /documents/{filename}.
  // ---------------------------------------------------------------------
  async function fetchDocuments() {
    try {
      const res = await fetch("/documents");
      if (!res.ok) throw new Error("Failed to load documents");
      const docs = await res.json();
      renderDocList(docs);
    } catch (err) {
      console.error(err);
      renderDocsUnavailable();
    }
  }

  function renderDocList(docs) {
    el.docList.querySelectorAll(".doc-item").forEach((n) => n.remove());
    const note = el.docList.querySelector(".doc-list-note");
    if (note) note.remove();

    el.docEmpty.hidden = docs && docs.length > 0;

    (docs || []).forEach((doc) => {
      const filename = doc.filename;
      const chunkLabel = (typeof doc.chunks === "number") ? `${doc.chunks} chunk${doc.chunks === 1 ? "" : "s"}` : "";
      const item = document.createElement("div");
      item.className = "doc-item";
      item.innerHTML = `
        <span class="doc-icon">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none"><path d="M4 2h5l3 3v9a1 1 0 01-1 1H4a1 1 0 01-1-1V3a1 1 0 011-1z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/><path d="M9 2v3h3" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></svg>
        </span>
        <span class="doc-name" title="${escapeHtml(filename)}">${escapeHtml(filename)}</span>
        ${chunkLabel ? `<span class="doc-meta">${escapeHtml(chunkLabel)}</span>` : ""}
        <button class="doc-delete-btn" title="Remove document" aria-label="Remove ${escapeHtml(filename)}">
          <svg width="13" height="13" viewBox="0 0 16 16" fill="none"><path d="M3 5h10M6.5 5V3.5A1 1 0 017.5 2.5h1A1 1 0 019.5 3.5V5M7 8v4M9 8v4M4 5l.6 8a1 1 0 001 .9h4.8a1 1 0 001-.9L12 5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </button>
      `;
      item.querySelector(".doc-delete-btn").addEventListener("click", () => deleteDocument(filename, item));
      el.docList.appendChild(item);
    });
  }

  function renderDocsUnavailable() {
    el.docList.querySelectorAll(".doc-item").forEach((n) => n.remove());
    el.docEmpty.hidden = true;
    if (!el.docList.querySelector(".doc-list-note")) {
      const note = document.createElement("div");
      note.className = "doc-list-note";
      note.textContent = "Couldn't load the document list.";
      el.docList.appendChild(note);
    }
  }

  async function deleteDocument(filename, itemEl) {
    const deleteBtn = itemEl.querySelector(".doc-delete-btn");
    deleteBtn.disabled = true;
    try {
      const res = await fetch(`/documents/${encodeURIComponent(filename)}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Failed to delete document");
      itemEl.remove();
      if (!el.docList.querySelector(".doc-item")) el.docEmpty.hidden = false;
    } catch (err) {
      console.error(err);
      deleteBtn.disabled = false;
      setUploadStatus(`Couldn't remove ${filename}.`, "error");
    }
  }

  el.refreshDocsBtn.addEventListener("click", fetchDocuments);

  // ---------------------------------------------------------------------
  // Init
  // ---------------------------------------------------------------------
  toggleWelcome();
  fetchConversations();
  fetchDocuments();
})();
