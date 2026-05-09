/**
 * Documentation module barrel — exports all public components and utilities.
 */
export { DocumentationViewer } from './DocumentationViewer';
export { DocumentationContent } from './DocumentationContent';
export { MermaidDiagram } from './MermaidDiagram';
export { DOC_CATALOG, DOC_CATEGORIES, getDocById, getDocsByCategory } from './documentation-data';
export type { DocEntry } from './documentation-data';
export { searchDocs, invalidateSearchCache } from './documentation-search';
export type { SearchResult } from './documentation-search';
