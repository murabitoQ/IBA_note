// -----------------------------
// 分頁切換
// -----------------------------
const navLinks = document.querySelectorAll('.nav-link');
const sections = document.querySelectorAll('.page-section');

navLinks.forEach(link => {
    link.addEventListener('click', () => {
        const page = link.dataset.page;
        sections.forEach(sec => sec.classList.add('d-none'));
        document.getElementById(`page-${page}`).classList.remove('d-none');
        navLinks.forEach(n => n.classList.remove('active'));
        link.classList.add('active');
    });
});

// -----------------------------
// IC / RC 圖片選擇與 Note 區塊
// -----------------------------
let selectedIC = new Set();
let selectedRC = new Set();

function toggleSelection(type, folderName, imgElement) {
    const set = type === "IC" ? selectedIC : selectedRC;
    if (set.has(folderName)) {
        set.delete(folderName);
        imgElement.classList.remove("selected");
    } else {
        set.add(folderName);
        imgElement.classList.add("selected");
    }
    renderAllNoteBlocks();
}

// -----------------------------
// 渲染 Note-block 與留言區
// -----------------------------
async function renderAllNoteBlocks() {
    await renderNoteBlocks("IC", Array.from(selectedIC));
    await renderNoteBlocks("RC", Array.from(selectedRC));
}

async function renderNoteBlocks(type, images) {
    const containerId = type === "IC" ? "ic-note-blocks" : "rc-note-blocks";
    const container = document.getElementById(containerId);
    container.innerHTML = "";

    for (let img_src of images) {
        // 取得資料
        const res = await fetch(`/api/note/${type}`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ image_src: img_src })
        });
        const data = await res.json();

        // 建立 note-block
        const block = document.createElement("div");
        block.className = "note-block";

        // 內容區
        const content = document.createElement("div");
        content.className = "note-content";
        content.innerHTML = `
            <img src="${data.data_content.img_path}" alt="img">
            <strong>${data.data_content.jp_name || data.data_content.info || ''}</strong>
            <p>${data.data_content.caption || ''}</p>
        `;

        block.appendChild(content);
        container.appendChild(block);

// -----------------------------
// 初始化留言區
// -----------------------------
        // 留言容器
        const chatContainer = document.createElement("div");
        chatContainer.className = "chat-container mt-2";
        chatContainer.style.display = "none"; // 預設隱藏

        // --- 新增留言區 ---
        const newChat = document.createElement("div");
        newChat.className = "chat-new d-flex flex-column flex-md-row align-items-start gap-2 mb-2";

        const textarea = document.createElement("textarea");
        textarea.className = "form-control chat-input flex-grow-1";
        textarea.rows = 2;

        const addBtn = document.createElement("button");
        addBtn.className = "btn btn-success btn-sm flex-shrink-0";
        addBtn.textContent = "➕";

        newChat.append(textarea, addBtn);
        chatContainer.appendChild(newChat);

        // --- 歷史留言區 ---
        const logList = document.createElement("div");
        logList.className = "chat-log-list";
        chatContainer.appendChild(logList);

        content.after(chatContainer);

        // 顯示 / 隱藏留言
        content.onclick = () => {
            chatContainer.style.display = chatContainer.style.display === "none" ? "block" : "none";
        };

        // 新增留言事件
        addBtn.onclick = async () => {
            if (!textarea.value.trim()) return;
            await fetch("/chat/add", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ image_src: img_src, text: textarea.value })
            });
            textarea.value = "";
            await refreshChatLog();
        };

        // 重新渲染留言列表
        async function refreshChatLog() {
            logList.innerHTML = "";
            const logs = await fetch(`/api/note/${type}`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ image_src: img_src })
            }).then(r => r.json()).then(j => j.chat_log);

            // 由新到舊
            logs.sort((a,b) => new Date(b.timestamp) - new Date(a.timestamp));

            logs.forEach(entry => {
                const item = document.createElement("div");
                item.className = "chat-entry d-flex justify-content-between align-items-start gap-2 mb-1";

                // 留言文字
                const textSpan = document.createElement("span");
                textSpan.className = "chat-text flex-grow-1";
                textSpan.style.whiteSpace = "pre-wrap";
                textSpan.textContent = entry.content;

                // 時間 + 編輯/刪除按鈕
                const btnGroup = document.createElement("div");
                btnGroup.className = "d-flex gap-1 flex-shrink-0 flex-column flex-md-row align-items-start";

                const timeSpan = document.createElement("span");
                timeSpan.className = "chat-time text-muted small";
                timeSpan.textContent = entry.timestamp;

                const editBtn = document.createElement("button");
                editBtn.className = "btn btn-primary btn-sm";
                editBtn.textContent = "📝";

                const deleteBtn = document.createElement("button");
                deleteBtn.className = "btn btn-danger btn-sm";
                deleteBtn.textContent = "🗑️";
                btnGroup.append(timeSpan, editBtn, deleteBtn);
                item.append(textSpan, btnGroup);
                logList.appendChild(item);

                // 編輯
                editBtn.onclick = () => {
                    const editContainer = document.createElement("div");
                    editContainer.className = "chat-new d-flex flex-column flex-md-row align-items-start gap-2 mb-1";

                    const editArea = document.createElement("textarea");
                    editArea.className = "form-control chat-input";
                    editArea.rows = 3;
                    editArea.value = entry.content;

                    const btnGroupEdit = document.createElement("div");
                    btnGroupEdit.className = "d-flex gap-1 flex-shrink-0";
                    
                    const saveBtn = document.createElement("button");
                    saveBtn.className = "btn btn-success btn-sm";
                    saveBtn.textContent = "💾";

                    const cancelBtn = document.createElement("button");
                    cancelBtn.className = "btn btn-secondary btn-sm";
                    cancelBtn.textContent = "❌";

                    btnGroupEdit.append(saveBtn, cancelBtn);

                    // **正確做法：textarea 放在 editContainer，btnGroupEdit 放右側**
                    editContainer.append(editArea, btnGroupEdit);
                    item.innerHTML = "";
                    item.appendChild(editContainer);

                    saveBtn.onclick = async () => {
                        await fetch("/chat/update", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({
                                image_src: img_src,
                                original_timestamp: entry.timestamp,
                                new_content: editArea.value
                            })
                        });
                        await refreshChatLog();
                    };
                    //取消
                    cancelBtn.onclick = () => refreshChatLog();
                };

                // 刪除
                deleteBtn.onclick = async () => {
                    if (!confirm("確定要刪除這則留言？")) return;
                    await fetch("/chat/delete", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ image_src: img_src, timestamp: entry.timestamp })
                    });
                    await refreshChatLog();
                };
            });
        }

        refreshChatLog();
    }
}
// -----------------------------
// 渲染 IC / RC 最新圖片
// -----------------------------
async function renderGallery(type, containerId) {
    const container = document.getElementById(containerId);
    const res = await fetch(`/api/${type.toLowerCase()}_latest`);
    const data = await res.json();
    container.innerHTML = "";

    data.forEach(item => {
        const div = document.createElement("div");
        div.className = "image-card";
        div.innerHTML = `
            <img src="${item.image}" alt="${item.folder}" data-folder="${item.folder}">
            <span class="folder-label">${item.folder}</span>
        `;
        const imgEl = div.querySelector("img");
        imgEl.onclick = () => toggleSelection(type, item.folder, imgEl);
        container.appendChild(div);
    });
}

renderGallery("IC", "ic-gallery");
renderGallery("RC", "rc-gallery");

// -----------------------------
// Guide & Set 更新 DB
// -----------------------------
/*
document.getElementById('update-db-btn').addEventListener('click', () => {
    const url = document.getElementById('db-url-input').value || "https://imaginary-base.jp/cast/";
    const logDiv = document.getElementById('update-log');
    logDiv.innerHTML = "";
    const eventSource = new EventSource(`/api/update_db?url=${encodeURIComponent(url)}`);
    eventSource.onmessage = (e) => {
        const p = document.createElement('p');
        p.textContent = e.data;
        logDiv.appendChild(p);
        logDiv.scrollTop = logDiv.scrollHeight;
    };
    eventSource.onerror = () => eventSource.close();
});
*/
// -----------------------------
// 語言切換
// -----------------------------
/*
const textMap = {
    zh: {
        'nav-title': 'DB Editor', 'nav-ic': 'IC', 'nav-rc': 'RC', 'nav-note': 'Note', 'nav-guide': 'Guide & Set',
        'ic-title': 'IC', 'ic-desc': '此區將顯示與編輯 IC 資料。',
        'rc-title': 'RC', 'rc-desc': '此區將顯示與編輯 RC 資料。',
        'note-title': 'Note', 'ic-note-title': 'IC 相關資料', 'rc-note-title': 'RC 相關資料',
        'guide-title': 'Guide & Set', 'tutorial-title': '教學網頁', 'update-db-title': '更新 DB', 'language-title': '語言選擇'
    },
    en: {
        'nav-title': 'DB Editor', 'nav-ic': 'IC', 'nav-rc': 'RC', 'nav-note': 'Note', 'nav-guide': 'Guide & Set',
        'ic-title': 'IC', 'ic-desc': 'This section displays and edits IC data.',
        'rc-title': 'RC', 'rc-desc': 'This section displays and edits RC data.',
        'note-title': 'Note', 'ic-note-title': 'IC Related Data', 'rc-note-title': 'RC Related Data',
        'guide-title': 'Guide & Set', 'tutorial-title': 'Tutorial Pages', 'update-db-title': 'Update DB', 'language-title': 'Language Selection'
    },
    jp: {
        'nav-title': 'DBエディタ', 'nav-ic': 'IC', 'nav-rc': 'RC', 'nav-note': 'ノート', 'nav-guide': 'ガイド & 設定',
        'ic-title': 'IC', 'ic-desc': 'このセクションはICデータを表示および編集します。',
        'rc-title': 'RC', 'rc-desc': 'このセクションはRCデータを表示および編集します。',
        'note-title': 'ノート', 'ic-note-title': 'IC 関連データ', 'rc-note-title': 'RC 関連データ',
        'guide-title': 'ガイド & 設定', 'tutorial-title': 'チュートリアルページ', 'update-db-title': 'DB更新', 'language-title': '言語選択'
    }
};
document.getElementById('language-select').addEventListener('change', () => {
    const lang = document.getElementById('language-select').value;
    for (const id in textMap[lang]) {
        const el = document.getElementById(id);
        if(el) el.textContent = textMap[lang][id];
    }
});
*/