/**
 * Lightweight markdown-to-HTML renderer.
 * Handles: headings, bold, italic, inline code, fenced code blocks,
 * unordered/ordered lists, tables, blockquotes, links, horizontal rules.
 */

export function renderMarkdown(text) {
  if (!text) return '';

  const lines = text.split('\n');
  const output = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // ── Fenced code block ──────────────────────────────────────
    if (line.startsWith('```')) {
      const lang = line.slice(3).trim() || '';
      const codeLines = [];
      i++;
      while (i < lines.length && !lines[i].startsWith('```')) {
        codeLines.push(escHtml(lines[i]));
        i++;
      }
      const langLabel = lang ? `<span class="code-lang">${escHtml(lang)}</span>` : '';
      output.push(
        `<div class="code-block-wrap">${langLabel}<pre class="code-block"><code>${codeLines.join('\n')}</code></pre></div>`
      );
      i++;
      continue;
    }

    // ── Heading ────────────────────────────────────────────────
    const headingMatch = line.match(/^(#{1,3})\s+(.+)$/);
    if (headingMatch) {
      const level = headingMatch[1].length;
      output.push(`<h${level}>${inlineMarkdown(headingMatch[2])}</h${level}>`);
      i++;
      continue;
    }

    // ── Horizontal rule ────────────────────────────────────────
    if (/^[-*]{3,}$/.test(line.trim())) {
      output.push('<hr />');
      i++;
      continue;
    }

    // ── Blockquote ─────────────────────────────────────────────
    if (line.startsWith('> ')) {
      const quoteLines = [];
      while (i < lines.length && lines[i].startsWith('> ')) {
        quoteLines.push(inlineMarkdown(lines[i].slice(2)));
        i++;
      }
      output.push(`<blockquote>${quoteLines.join('<br />')}</blockquote>`);
      continue;
    }

    // ── Unordered list ─────────────────────────────────────────
    if (/^[-*+]\s/.test(line)) {
      const items = [];
      while (i < lines.length && /^[-*+]\s/.test(lines[i])) {
        items.push(`<li>${inlineMarkdown(lines[i].replace(/^[-*+]\s/, ''))}</li>`);
        i++;
      }
      output.push(`<ul>${items.join('')}</ul>`);
      continue;
    }

    // ── Ordered list ───────────────────────────────────────────
    if (/^\d+\.\s/.test(line)) {
      const items = [];
      while (i < lines.length && /^\d+\.\s/.test(lines[i])) {
        items.push(`<li>${inlineMarkdown(lines[i].replace(/^\d+\.\s/, ''))}</li>`);
        i++;
      }
      output.push(`<ol>${items.join('')}</ol>`);
      continue;
    }

    // ── Table ──────────────────────────────────────────────────
    if (line.includes('|') && i + 1 < lines.length && /^\|[-|\s:]+\|/.test(lines[i + 1])) {
      const headers = parseCells(line);
      i += 2; // skip separator
      const rows = [];
      while (i < lines.length && lines[i].includes('|')) {
        rows.push(parseCells(lines[i]));
        i++;
      }
      const thead = `<thead><tr>${headers.map(h => `<th>${inlineMarkdown(h)}</th>`).join('')}</tr></thead>`;
      const tbody = `<tbody>${rows.map(row =>
        `<tr>${row.map(cell => `<td>${inlineMarkdown(cell)}</td>`).join('')}</tr>`
      ).join('')}</tbody>`;
      output.push(`<table>${thead}${tbody}</table>`);
      continue;
    }

    // ── Blank line ─────────────────────────────────────────────
    if (line.trim() === '') {
      i++;
      continue;
    }

    // ── Paragraph ─────────────────────────────────────────────
    const paraLines = [];
    while (
      i < lines.length &&
      lines[i].trim() !== '' &&
      !/^#{1,3}\s/.test(lines[i]) &&
      !/^[-*+]\s/.test(lines[i]) &&
      !/^\d+\.\s/.test(lines[i]) &&
      !lines[i].startsWith('```') &&
      !lines[i].startsWith('> ')
    ) {
      paraLines.push(inlineMarkdown(lines[i]));
      i++;
    }
    if (paraLines.length) {
      output.push(`<p>${paraLines.join(' ')}</p>`);
    }
  }

  return output.join('\n');
}

// ── Inline markdown (bold, italic, code, links) ───────────────
function inlineMarkdown(text) {
  let t = escHtml(text);

  // Bold + italic
  t = t.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
  // Bold
  t = t.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  t = t.replace(/__(.+?)__/g, '<strong>$1</strong>');
  // Italic
  t = t.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  t = t.replace(/_([^_]+)_/g, '<em>$1</em>');
  // Inline code
  t = t.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');
  // Links
  t = t.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');

  return t;
}

function escHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function parseCells(row) {
  return row.split('|').map(c => c.trim()).filter((c, i, arr) => i > 0 && i < arr.length - 1 || c !== '');
}
