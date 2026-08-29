async function loadChapters() {
  try {
    const response = await fetch('/api/chapters');
    const chapters = await response.json();
    
    const container = document.getElementById('chapter-items');
    chapters.forEach((chapter, index) => {
      const item = document.createElement('div');
      item.className = 'draggable-item';
      item.draggable = true;
      item.innerHTML = `
        <span>${chapter.number}</span>
        <span>${chapter.title}</span>
        <span>${chapter.words} words</span>
      `;
      item.dataset.index = index;
      container.appendChild(item);
    });
    
    setupDragAndDrop(container);
  } catch (error) {
    console.error('Failed to load chapters:', error);
  }
}

function setupDragAndDrop(container) {
  let draggedItem = null;
  
  container.addEventListener('dragstart', (e) => {
    draggedItem = e.target;
    setTimeout(() => e.target.classList.add('dragging'), 0);
  });
  
  container.addEventListener('dragend', (e) => {
    e.target.classList.remove('dragging');
    draggedItem = null;
    saveOrder();
  });
  
  container.addEventListener('dragover', (e) => {
    e.preventDefault();
    const afterElement = getDragAfterElement(container, e.clientY);
    const draggable = draggedItem;
    if (afterElement == null) {
      container.appendChild(draggable);
    } else {
      container.insertBefore(draggable, afterElement);
    }
  });
}

function getDragAfterElement(container, y) {
  const draggableElements = [...container.querySelectorAll('.draggable-item:not(.dragging)')];
  
  return draggableElements.reduce((closest, child) => {
    const box = child.getBoundingClientRect();
    const offset = y - box.top - box.height / 2;
    if (offset < 0 && offset > closest.offset) {
      return { offset: offset, element: child };
    } else {
      return closest;
    }
  }, { offset: Number.NEGATIVE_INFINITY }).element;
}

function saveOrder() {
  const chapters = Array.from(document.getElementById('chapter-items').children);
  const order = chapters.map(item => item.dataset.index);
  localStorage.setItem('chapter-order', JSON.stringify(order));
  alert('Order saved! Changes will apply on build.');
}

// Initialize
document.addEventListener('DOMContentLoaded', loadChapters);
