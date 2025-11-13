/**
 * Type definitions for mkdocs-exam JavaScript
 */

/**
 * Extend HTMLElement to include custom properties
 */
interface HTMLElement {
  /**
   * Custom property to store the save state function for an exam
   */
  _saveState?: () => void;
}

/**
 * Extend Element dataset to include exam-specific data attributes
 */
interface DOMStringMap {
  type?: string;
  points?: string;
  timeLimit?: string;
  partialCredit?: string;
  feedback?: string;
  weight?: string;
  correct?: string;
  penalty?: string;
  show?: string;
  itemIndex?: string;
  correctCategory?: string;
  categoryIndex?: string;
  regionIndex?: string;
  index?: string;
  correctOrder?: string;
  tolerance?: string;
}
