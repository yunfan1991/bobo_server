import './chunk-f2006744.js';
import './chunk-7b019b33.js';
import './chunk-b170726a.js';
import './chunk-1d58fda4.js';
import { r as registerComponent, u as use } from './chunk-cca88db8.js';
import { P as Pagination, a as PaginationButton } from './chunk-33e98d0a.js';
export { P as BPagination, a as BPaginationButton } from './chunk-33e98d0a.js';

var Plugin = {
  install: function install(Vue) {
    registerComponent(Vue, Pagination);
    registerComponent(Vue, PaginationButton);
  }
};
use(Plugin);

export default Plugin;
