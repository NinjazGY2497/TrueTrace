import { requestBackend } from "./requestBackend.js";

let currentMode = 'text';

function switchMode(mode) {
    currentMode = mode;

    document.getElementById('textSection').classList.toggle('hidden', mode !== 'text');
    document.getElementById('imageSection').classList.toggle('hidden', mode !== 'image');
    document.getElementById('resultsSection').classList.add('hidden');

    document.getElementById('btnText').classList.toggle('active', mode === 'text');
    document.getElementById('btnImage').classList.toggle('active', mode === 'image');
}

async function showResults(mode) {
    document.getElementById('textSection').classList.add('hidden');
    document.getElementById('imageSection').classList.add('hidden');

    try {
        let data = await requestBackend(mode);

        const confidence = Math.round(data["confidence"] * 100);
        const isAI = (data["label"].toLowerCase() === "human") ? false : true;
        console.log(confidence, isAI)
        const bar = document.getElementById('confidenceBar');
        bar.style.setProperty('--bar-width', confidence + '%');
        bar.style.width = '0%';
        void bar.offsetWidth;
        bar.style.width = confidence + '%';

        document.getElementById('confidencePct').textContent = confidence + '%';

        const badge = document.getElementById('resultBadge');
        badge.textContent = isAI ? 'AI Generated' : 'Likely Human';
        badge.className = 'result-badge ' + (isAI ? 'ai' : 'human');

        const breakdownList = document.getElementById('breakdownList');
        breakdownList.innerHTML = '';

        if (Array.isArray(data.reasons) && data.reasons.length > 0) {
            data.reasons.forEach(reason => {
                const item = document.createElement('div');
                item.className = 'breakdown-item';
                item.textContent = reason;
                breakdownList.appendChild(item);
            });
        } else {
            breakdownList.textContent = 'No explanation available.';
        }

        document.getElementById('resultsSection').classList.remove('hidden');
    } catch (error) {
        console.error('Analysis failed:', error);
        alert('Analysis failed. Please check that the backend is running and the browser console for details.');
        document.getElementById('textSection').classList.toggle('hidden', mode !== 'text');
        document.getElementById('imageSection').classList.toggle('hidden', mode !== 'image');
    }
}

function goBack() {
    document.getElementById('resultsSection').classList.add('hidden');
    switchMode(currentMode);
}

window.switchMode = switchMode;
window.showResults = showResults;
window.goBack = goBack;