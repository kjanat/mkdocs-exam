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

/**
 * Type guard to check if an element is an HTMLElement
 */
declare function isHTMLElement(element: Element | null): element is HTMLElement;

/**
 * Type guard to check if an element is an HTMLInputElement
 */
declare function isHTMLInputElement(
  element: Element | null,
): element is HTMLInputElement;

/**
 * Type guard to check if an element is an HTMLButtonElement
 */
declare function isHTMLButtonElement(
  element: Element | null,
): element is HTMLButtonElement;

/**
 * Type guard to check if an element is an HTMLSelectElement
 */
declare function isHTMLSelectElement(
  element: Element | null,
): element is HTMLSelectElement;

/**
 * Type guard to check if an element is an HTMLFieldSetElement
 */
declare function isHTMLFieldSetElement(
  element: Element | null,
): element is HTMLFieldSetElement;
