// Resolve repository files outside the docs content root before Docusaurus's
// default link resolver. Repository Markdown remains usable on GitHub/local disk.
const fs = require('node:fs');
const path = require('node:path');

module.exports = function remarkRepositoryLinks() {
  const root = path.resolve(__dirname, '../..');
  const docs = path.join(root, 'docs');
  const excluded = path.join(docs, 'history');
  return (tree, file) => {
    function visit(node) {
      if ((node.type === 'link' || node.type === 'definition') &&
          node.url && !/^(?:[a-z]+:|\/|#)/i.test(node.url)) {
        const [target, fragment = ''] = node.url.split('#', 2);
        const resolved = path.resolve(path.dirname(file.path), target);
        const relative = path.relative(root, resolved);
        const inDocs = (resolved === docs || resolved.startsWith(docs + path.sep)) &&
          resolved !== excluded && !resolved.startsWith(excluded + path.sep);
        if (!inDocs && !relative.startsWith('..') && fs.existsSync(resolved)) {
          const kind = fs.statSync(resolved).isDirectory() ? 'tree' : 'blob';
          const encoded = relative.split(path.sep).map(encodeURIComponent).join('/');
          node.url = `https://github.com/datenoio/internacia-db/${kind}/main/${encoded}${fragment ? '#' + fragment : ''}`;
        }
      }
      for (const child of node.children || []) visit(child);
    }
    visit(tree);
  };
};
