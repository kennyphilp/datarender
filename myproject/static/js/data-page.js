// Clean, self-contained frontend for data page
const STORAGE_KEY = 'school-data-page-selections:v1';

// Configuration constants (matches backend constants.py)
const DEFAULT_PAGE_SIZE = 200;
const MAX_RETRY_ATTEMPTS = 3;
const RETRY_DELAY_MS = 1000;

const state = {
  allData: [],
  currentData: [],
  currentColumns: [],
  currentSort: { column: null, direction: 'asc' },
  page: 1,
  page_size: DEFAULT_PAGE_SIZE,
  total: 0,
  total_pages: 1,
  // Client-side view pagination (how many rows the table shows per view)
  view_page: 1,
  view_page_size: 10,
  // Persist selections by ObjectId
  selectedIds: new Set(),
  selectedSectors: new Set(),
  selectedTypes: new Set(),
  // distinct lists from server
  distinct: { names: [], sectors: [], types: [] },
  isLoading: false,
  lastError: null,
};

const DOM = {
  nameList: () => document.getElementById('nameFilterList'),
  sectorList: () => document.getElementById('sectorFilterList'),
  typeList: () => document.getElementById('typeFilterList'),
  content: () => document.getElementById('content'),
  graphContent: () => document.getElementById('graph-content'),
  exportBtn: () => document.getElementById('exportGraphBtn'),
  errorContainer: () => document.getElementById('errorContainer'),
};

/**
 * Display user-friendly error message with optional retry button
 */
function showError(message, canRetry = false) {
  state.lastError = message;
  const errorHtml = `
    <div class="error-message" role="alert" aria-live="polite">
      <strong>Error:</strong> ${message}
      ${canRetry ? '<button class="retry-btn" onclick="retryLastOperation()">Retry</button>' : ''}
      <button class="dismiss-btn" onclick="dismissError()">×</button>
    </div>
  `;
  
  const container = DOM.errorContainer();
  if (container) {
    container.innerHTML = errorHtml;
    container.style.display = 'block';
  } else {
    // Fallback if error container doesn't exist
    const content = DOM.content();
    content.innerHTML = errorHtml + content.innerHTML;
  }
}

/**
 * Clear error message display
 */
function dismissError() {
  const container = DOM.errorContainer();
  if (container) {
    container.innerHTML = '';
    container.style.display = 'none';
  }
  state.lastError = null;
}

/**
 * Retry the last failed operation
 */
async function retryLastOperation() {
  dismissError();
  await loadPage(state.page, state.page_size);
}

/**
 * Fetch with automatic retry logic
 */
async function fetchWithRetry(url, options = {}, retries = MAX_RETRY_ATTEMPTS) {
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      const response = await fetch(url, options);
      if (!response.ok) {
        if (response.status >= 500 && attempt < retries) {
          // Server error - retry
          await new Promise(resolve => setTimeout(resolve, RETRY_DELAY_MS * attempt));
          continue;
        }
        throw new Error(`Server returned ${response.status}: ${response.statusText}`);
      }
      return response;
    } catch (error) {
      if (attempt === retries) {
        throw error;
      }
      // Network error - retry after delay
      await new Promise(resolve => setTimeout(resolve, RETRY_DELAY_MS * attempt));
    }
  }
}

function debounce(fn, wait = 150) {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), wait);
  };
}

function escapeHtml(unsafe) {
  if (unsafe === null || unsafe === undefined) return '';
  return String(unsafe)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function loadSavedSelections() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { ids: [], sectors: [], types: [] };
    const parsed = JSON.parse(raw);
    return {
      ids: Array.isArray(parsed.ids) ? parsed.ids : [],
      sectors: Array.isArray(parsed.sectors) ? parsed.sectors : [],
      types: Array.isArray(parsed.types) ? parsed.types : [],
    };
  } catch (e) {
    console.warn('Failed to load saved selections', e);
    return { ids: [], sectors: [], types: [] };
  }
}

function saveSelections() {
  try {
    const payload = {
      ids: Array.from(state.selectedIds),
      sectors: Array.from(state.selectedSectors),
      types: Array.from(state.selectedTypes),
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
  } catch (e) {
    console.warn('Failed to save selections', e);
  }
}

async function loadData() {
  // Kick off by loading first page
  console.log('[LOAD] loadData() started');
  try {
    await loadPage(1, DEFAULT_PAGE_SIZE);
    console.log('[LOAD] loadPage() completed successfully');
  } catch (error) {
    console.error('[LOAD] Error in loadData():', error);
    showError(`Failed to load data: ${error.message}`, true);
  }
}

async function loadPage(page = 1, pageSize = DEFAULT_PAGE_SIZE) {
  if (state.isLoading) {
    console.warn('[LOAD] Load already in progress, skipping duplicate request');
    return;
  }
  
  console.log('[LOAD] loadPage() started - page:', page, 'pageSize:', pageSize);
  state.isLoading = true;
  dismissError();
  
  try {
    const url = new URL('/api/data/', window.location.origin);
    url.searchParams.set('page', page);
    url.searchParams.set('page_size', pageSize);
    
    console.log('[LOAD] Fetching:', url.toString());
    const res = await fetchWithRetry(url.toString());
    console.log('[LOAD] Fetch completed, parsing JSON...');
    const result = await res.json();
    console.log('[LOAD] API response:', { 
      page: result.page, 
      total: result.total, 
      distinctNames: result.distinct?.names?.length,
      distinctSectors: result.distinct?.sectors?.length,
      distinctTypes: result.distinct?.types?.length
    });

    // Update pagination and distinct lists
    state.page = result.page || 1;
    state.page_size = result.page_size || pageSize;
    state.total = result.total || 0;
    state.total_pages = result.total_pages || 1;
    state.distinct = result.distinct || { names: [], sectors: [], types: [] };

    // Convert rows and keep ObjectId (normalize to string)
    state.allData = result.data.map(row => {
      const transformed = {};
      Object.keys(row).forEach(k => {
        if (['ObjectId','Code','LA_Code','LA_Name'].includes(k)) return;
        let nk = k === 'School_Type' ? 'School Type' : k;
        if (k.startsWith('F') && /^F\d{4}$/.test(k)) nk = k.substring(1);
        transformed[nk] = row[k];
      });
      transformed.ObjectId = row.ObjectId !== null && row.ObjectId !== undefined ? String(row.ObjectId) : '';
      return transformed;
    });

    state.currentData = [...state.allData];
    state.currentColumns = result.columns.filter(c => !['ObjectId','Code','LA_Code','LA_Name'].includes(c)).map(c => c === 'School_Type' ? 'School Type' : (c.startsWith('F') ? c.substring(1) : c));

    // Load saved selections (ids) and populate filters
    const saved = loadSavedSelections();
    state.selectedIds = new Set((saved.ids || []).map(id => String(id)));
    state.selectedSectors = new Set(saved.sectors);
    state.selectedTypes = new Set(saved.types);

    // Populate filters using distinct lists when available
    console.log('[LOAD] Populating filters...');
    const nameList = DOM.nameList();
    const sectorList = DOM.sectorList();
    const typeList = DOM.typeList();
    
    console.log('[LOAD] DOM elements:', {
      nameList: !!nameList,
      sectorList: !!sectorList,
      typeList: !!typeList
    });
    
    if (Array.isArray(state.distinct.names) && state.distinct.names.length > 0) {
      console.log('[LOAD] Populating', state.distinct.names.length, 'school names');
      // Ensure distinct ids are strings
      const namesWithStringIds = state.distinct.names.map(x => ({ id: String(x.id), name: x.name }));
      populateNameFilterFromDistinct(nameList, namesWithStringIds, 'name', handleNameFilter, state.selectedIds);
    } else {
      console.log('[LOAD] Using fallback for name filter');
      // Fallback: we only have current page names. Map selectedIds to names so checked state can be preserved
      const idToName = new Map(state.allData.map(r => [String(r.ObjectId), r.Name]));
      const selectedNamesFromIds = new Set(Array.from(state.selectedIds).map(id => idToName.get(String(id))).filter(Boolean));
      populateFilter(nameList, [...new Set(state.allData.map(r => r.Name))].sort(), 'name', handleNameFilter, selectedNamesFromIds);
    }
    
    console.log('[LOAD] Populating', state.distinct.sectors?.length || 0, 'sectors');
    populateFilter(sectorList, Array.isArray(state.distinct.sectors) && state.distinct.sectors.length > 0 ? state.distinct.sectors : [...new Set(state.allData.map(r => r.Sector).filter(Boolean))].sort(), 'sector', handleSectorFilter, state.selectedSectors);
    
    console.log('[LOAD] Populating', state.distinct.types?.length || 0, 'types');
    populateFilter(typeList, Array.isArray(state.distinct.types) && state.distinct.types.length > 0 ? state.distinct.types : [...new Set(state.allData.map(r => r['School Type']).filter(Boolean))].sort(), 'type', handleTypeFilter, state.selectedTypes);

    console.log('[LOAD] Filters populated, displaying data...');
    displayData(state.currentColumns, state.currentData);
    console.log('[LOAD] Data displayed, updating graph...');
    updateGraph();
    console.log('[LOAD] Graph updated');

    const pageInfo = document.getElementById('pageInfo');
    if (pageInfo) pageInfo.textContent = `Page: ${state.page} of ${state.total_pages || 1}`;
    console.log('[LOAD] loadPage() completed successfully');
  } catch (err) {
    console.error('[LOAD] Failed to load data:', err);
    showError(`Unable to load school data. ${err.message}`, true);
    DOM.content().innerHTML = `<div class="error">Error loading data: ${err.message}</div>`;
  } finally {
    state.isLoading = false;
  }
}

function gotoNextPage(){ if(state.page < state.total_pages) loadPage(state.page + 1, state.page_size); }
function gotoPrevPage(){ if(state.page > 1) loadPage(state.page - 1, state.page_size); }

// View pagination for table rows (client-side)
function gotoNextViewPage(){
  const max = Math.ceil(state.currentData.length / state.view_page_size) || 1;
  if(state.view_page < max){ state.view_page += 1; displayData(state.currentColumns, state.currentData); updatePageInfo(); }
}

function gotoPrevViewPage(){
  if(state.view_page > 1){ state.view_page -= 1; displayData(state.currentColumns, state.currentData); updatePageInfo(); }
}

function updatePageInfo(){
  const el = document.getElementById('pageInfo');
  const max = Math.ceil(state.currentData.length / state.view_page_size) || 1;
  if(el) el.textContent = `Page: ${state.view_page} of ${max}`;
}

function populateFilter(container, values, prefix, changeHandler, selectedSet = null) {
  // selectedSet is an optional Set of values that should be checked initially
  const frag = document.createDocumentFragment();
  const prev = selectedSet instanceof Set ? selectedSet : new Set(Array.from(container.querySelectorAll('input[type="checkbox"]:checked')).map(cb => cb.value));
  container.innerHTML = '';
  values.forEach(v => {
    const id = `${prefix}_ck_${encodeURIComponent(v)}`;
    const label = document.createElement('label');
    label.htmlFor = id;
    const cb = document.createElement('input'); cb.type = 'checkbox'; cb.id = id; cb.value = v;
    cb.addEventListener('change', changeHandler);
    if (prev.has(v)) cb.checked = true;
    label.appendChild(cb);
    label.appendChild(document.createTextNode(v));
    frag.appendChild(label);
  });
  container.appendChild(frag);
}

function populateNameFilterFromDistinct(container, items, prefix, changeHandler, selectedSet = null) {
  // items: [{id, name}, ...]
  const frag = document.createDocumentFragment();
  const prev = selectedSet instanceof Set ? selectedSet : new Set(Array.from(container.querySelectorAll('input[type="checkbox"]:checked')).map(cb => cb.value));
  container.innerHTML = '';
  items.forEach(item => {
    const id = `${prefix}_ck_${encodeURIComponent(item.id)}`;
    const label = document.createElement('label');
    label.htmlFor = id;
    const cb = document.createElement('input'); cb.type = 'checkbox'; cb.id = id; cb.value = item.id; cb.setAttribute('data-name', item.name);
    cb.addEventListener('change', changeHandler);
    if (prev.has(item.id) || prev.has(item.name)) cb.checked = true;
    label.appendChild(cb);
    label.appendChild(document.createTextNode(item.name));
    frag.appendChild(label);
  });
  container.appendChild(frag);
}

function handleNameFilter() {
  state.selectedIds = new Set(Array.from(DOM.nameList().querySelectorAll('input:checked')).map(cb=>String(cb.value)));
  updateSelectedCount();
  saveSelections();
  applyFilters();
}
function handleSectorFilter() { state.selectedSectors = new Set(Array.from(DOM.sectorList().querySelectorAll('input:checked')).map(cb=>cb.value)); updateSectorCount(); saveSelections(); applyFilters(); }
function handleTypeFilter() { state.selectedTypes = new Set(Array.from(DOM.typeList().querySelectorAll('input:checked')).map(cb=>cb.value)); updateTypeCount(); saveSelections(); applyFilters(); }

function updateSelectedCount(){ const count=state.selectedIds.size; const total= (state.distinct && state.distinct.names && state.distinct.names.length) ? state.distinct.names.length : [...new Set(state.allData.map(r=>r.Name))].length; const el=document.getElementById('selectedCount'); el.textContent = count===0 ? 'No schools selected (showing all)' : (count===total? 'All schools selected' : `${count} of ${total} schools selected`); }
function updateSectorCount(){ const count=state.selectedSectors.size; const total= state.distinct && state.distinct.sectors ? state.distinct.sectors.length : [...new Set(state.allData.map(r=>r.Sector))].length; const el=document.getElementById('sectorCount'); el.textContent = count===0? 'No sectors selected (showing all)' : (count===total? 'All sectors selected' : `${count} of ${total} sectors selected`); }
function updateTypeCount(){ const count=state.selectedTypes.size; const total= state.distinct && state.distinct.types ? state.distinct.types.length : [...new Set(state.allData.map(r=>r['School Type']))].length; const el=document.getElementById('typeCount'); el.textContent = count===0? 'No types selected (showing all)' : (count===total? 'All types selected' : `${count} of ${total} types selected`); }

function selectAll(container){ container.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked=true); }
function clearAll(container){ container.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked=false); }
function selectAllSchools(){ selectAll(DOM.nameList()); handleNameFilter(); saveSelections(); }
function clearAllSchools(){ clearAll(DOM.nameList()); handleNameFilter(); saveSelections(); }
function selectAllSectors(){ selectAll(DOM.sectorList()); handleSectorFilter(); saveSelections(); }
function clearAllSectors(){ clearAll(DOM.sectorList()); handleSectorFilter(); saveSelections(); }
function selectAllTypes(){ selectAll(DOM.typeList()); handleTypeFilter(); saveSelections(); }
function clearAllTypes(){ clearAll(DOM.typeList()); handleTypeFilter(); saveSelections(); }

function applyFilters(){
  state.currentData = state.allData.filter(row => {
    // if there are any selected ids, require the row.ObjectId be in that set
    if (state.selectedIds.size > 0 && !state.selectedIds.has(String(row.ObjectId))) return false;
    if (state.selectedSectors.size > 0 && !state.selectedSectors.has(row.Sector)) return false;
    if (state.selectedTypes.size > 0 && !state.selectedTypes.has(row['School Type'])) return false;
    return true;
  });
  if (state.currentSort.column) sortData(state.currentSort.column, false); else displayData(state.currentColumns, state.currentData);
  debouncedUpdateGraph();
}

const debouncedUpdateGraph = debounce(updateGraph, 120);

function updateGraph(){
  const graphContent = DOM.graphContent();
  if (!state.currentData || state.currentData.length===0){ 
    graphContent.innerHTML = '<div class="loading">No schools match the selected filters</div>'; 
    if(DOM.exportBtn()) DOM.exportBtn().disabled=true; 
    return; 
  }
  
  const visibleIds = new Set(state.currentData.map(r=>r.ObjectId));
  let selectedIds = state.selectedIds.size>0 ? Array.from(state.selectedIds).filter(id=>visibleIds.has(id)) : [...visibleIds];
  if (selectedIds.length===0){ 
    graphContent.innerHTML = '<div class="loading">No schools match the selected filters</div>'; 
    if(DOM.exportBtn()) DOM.exportBtn().disabled=true; 
    return; 
  }
  
  const params = new URLSearchParams(); 
  selectedIds.forEach(id=>params.append('ids', id));
  const graphUrl = `/api/enrollment-graph/?${params.toString()}`;
  let img = graphContent.querySelector('img'); 
  if(!img){ 
    img=document.createElement('img'); 
    graphContent.innerHTML=''; 
    graphContent.appendChild(img);
  } 
  img.src = graphUrl + '&t='+Date.now(); 
  img.alt = `Enrollment trends for ${selectedIds.length} selected school${selectedIds.length!==1?'s':''}`; 
  if(DOM.exportBtn()) DOM.exportBtn().disabled=false;
}

function sortData(column, toggleDirection=true){ 
  if(toggleDirection){ 
    if(state.currentSort.column===column) state.currentSort.direction = state.currentSort.direction==='asc' ? 'desc' : 'asc'; 
    else { state.currentSort.column = column; state.currentSort.direction='asc'; }
  } 
  state.currentData.sort((a,b)=>{ 
    let aVal=a[column], bVal=b[column]; 
    if(aVal==null) aVal=''; 
    if(bVal==null) bVal=''; 
    if(!isNaN(aVal) && !isNaN(bVal) && aVal!=='' && bVal!==''){ 
      aVal=parseFloat(aVal); 
      bVal=parseFloat(bVal);
    } else { 
      aVal=String(aVal).toLowerCase(); 
      bVal=String(bVal).toLowerCase(); 
    } 
    if(aVal<bVal) return state.currentSort.direction==='asc'?-1:1; 
    if(aVal>bVal) return state.currentSort.direction==='asc'?1:-1; 
    return 0; 
  }); 
  displayData(state.currentColumns, state.currentData); 
}

function displayData(columns, data){
  // Render only the slice for the current view page
  const start = (state.view_page - 1) * state.view_page_size;
  const end = start + state.view_page_size;
  const slice = data.slice(start, end);

  let html = '<table>';
  html += '<thead><tr>';
  columns.forEach(col => {
    const sortClass = state.currentSort.column===col ? (state.currentSort.direction==='asc' ? 'sorted-asc' : 'sorted-desc') : '';
    const isYearCol = /^\d{4}$/.test(col);
    const headerClass = isYearCol ? `year-col ${sortClass}`.trim() : sortClass;
    html += `<th class="${headerClass}" data-column="${col}" tabindex="0" role="button" aria-sort="${state.currentSort.column===col ? (state.currentSort.direction==='asc' ? 'ascending' : 'descending') : 'none'}">${col}</th>`;
  });
  html += '</tr></thead><tbody>';
  slice.forEach(row => {
    html += '<tr>';
    columns.forEach(col => {
      const value = row[col] !== null ? row[col] : '';
      const isYearCol = /^\d{4}$/.test(col);
      const isNameCol = col === 'Name';
      const isSectorCol = col === 'Sector';
      const isSchoolTypeCol = col === 'School Type';
      let cellClass = '';
      if (isYearCol) cellClass = 'year-col';
      else if (isNameCol) cellClass = 'name-col';
      else if (isSectorCol) cellClass = 'sector-col';
      else if (isSchoolTypeCol) cellClass = 'school-type-col';
      if (isNameCol) {
        const safe = escapeHtml(value);
        html += `<td class="${cellClass}"><span class="cell-name" title="${safe}">${safe}</span></td>`;
      } else {
        html += `<td class="${cellClass}">${escapeHtml(value)}</td>`;
      }
    });
    html += '</tr>';
  });
  html += '</tbody></table>';
  html += `<p style="margin-top: var(--spacing-md); color: var(--color-text-secondary);">Showing ${data.length} of ${state.total} schools (page ${state.page})</p>`;
  DOM.content().innerHTML = html;

  // Add click listeners to table headers for sorting
  DOM.content().querySelectorAll('th[data-column]').forEach(th => {
    th.addEventListener('click', () => sortData(th.dataset.column));
    th.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        sortData(th.dataset.column);
      }
    });
  });

  updatePageInfo();
}
function exportGraph() {
  console.log('[EXPORT] Export button clicked');
  const graphImg = DOM.graphContent()?.querySelector('img');
  if (!graphImg || !graphImg.src) {
    showError('No graph available to export', false);
    return;
  }
  
  try {
    // Create a temporary link element to trigger download
    const link = document.createElement('a');
    link.href = graphImg.src;
    link.download = `enrollment-trends-${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    console.log('[EXPORT] Graph exported successfully');
  } catch (error) {
    console.error('[EXPORT] Error exporting graph:', error);
    showError(`Failed to export graph: ${error.message}`, false);
  }
}

/**
 * Initialize event listeners when DOM is ready
 */
function initializeEventListeners() {
  // Filter button listeners
  document.getElementById('selectAllSchoolsBtn')?.addEventListener('click', selectAllSchools);
  document.getElementById('clearAllSchoolsBtn')?.addEventListener('click', clearAllSchools);
  document.getElementById('selectAllSectorsBtn')?.addEventListener('click', selectAllSectors);
  document.getElementById('clearAllSectorsBtn')?.addEventListener('click', clearAllSectors);
  document.getElementById('selectAllTypesBtn')?.addEventListener('click', selectAllTypes);
  document.getElementById('clearAllTypesBtn')?.addEventListener('click', clearAllTypes);
  
  // Pagination listeners - wire to client-side view pagination for table
  document.getElementById('prevPageBtn')?.addEventListener('click', gotoPrevViewPage);
  document.getElementById('nextPageBtn')?.addEventListener('click', gotoNextViewPage);
  
  // Export button listener
  document.getElementById('exportGraphBtn')?.addEventListener('click', exportGraph);
}

// Initialize when DOM is ready
function initializeApp() {
  try {
    console.log('[INIT] Initializing app...');
    initializeEventListeners();
    console.log('[INIT] Event listeners initialized');
    loadData();
    console.log('[INIT] loadData() called');
  } catch (error) {
    console.error('[INIT] Error during initialization:', error);
  }
}

// Check if DOM is already loaded (script at end of body)
console.log('[INIT] Script loaded, readyState:', document.readyState);
if (document.readyState === 'loading') {
  console.log('[INIT] Waiting for DOMContentLoaded...');
  document.addEventListener('DOMContentLoaded', initializeApp);
} else {
  console.log('[INIT] DOM already loaded, initializing now...');
  initializeApp();
}
