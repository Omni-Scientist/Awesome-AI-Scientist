// Runs awesome-lint's rule set with one rule disabled.
//
// This list uses the paper-list convention, `- [Name](url), "Paper Title".`,
// so the upstream rule that demands a dash between link and description does
// not apply. Every other awesome-lint rule still runs: dead links, duplicate
// links, table of contents matching the headings, heading structure, and so on.
//
//   npm i awesome-lint && node scripts/lint.mjs README.md
import {remark} from 'remark';
import {readSync} from 'to-vfile';
import reporter from 'vfile-reporter-pretty';
import config from 'awesome-lint/config.js';
import rules from 'awesome-lint/rules/index.js';

const DISABLED = new Set(['awesome-list-item']);
const idOf = plugin => (Array.isArray(plugin) ? plugin[0] : plugin)?.name?.replace(/^remark-lint:/, '');

const all = [...config, ...rules];
const active = all.filter(plugin => !DISABLED.has(idOf(plugin)));

const processor = remark();
for (const plugin of active) {
	Array.isArray(plugin) ? processor.use(...plugin) : processor.use(plugin);
}

const file = readSync(process.argv[2] ?? 'README.md');
const result = await processor.process(file);
const problems = result.messages.length;

console.log(`${active.length} rules active, ${all.length - active.length} disabled`);
console.log(reporter([result]) || 'no problems');
process.exit(problems > 0 ? 1 : 0);
