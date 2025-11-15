// ==================== Type Guards ====================

/**
 * Type guard to check if an element is an HTMLElement
 * @param {Element | null} element - The element to check
 * @returns {element is HTMLElement}
 */
function isHTMLElement(element) {
  return element !== null && element instanceof HTMLElement;
}

/**
 * Type guard to check if an element is an HTMLInputElement
 * @param {Element | null} element - The element to check
 * @returns {element is HTMLInputElement}
 */
function isHTMLInputElement(element) {
  return element !== null && element instanceof HTMLInputElement;
}

/**
 * Type guard to check if an element is an HTMLButtonElement
 * @param {Element | null} element - The element to check
 * @returns {element is HTMLButtonElement}
 */
function isHTMLButtonElement(element) {
  return element !== null && element instanceof HTMLButtonElement;
}

/**
 * Type guard to check if an element is an HTMLSelectElement
 * @param {Element | null} element - The element to check
 * @returns {element is HTMLSelectElement}
 */
function isHTMLSelectElement(element) {
  return element !== null && element instanceof HTMLSelectElement;
}

/**
 * Type guard to check if an element is an HTMLFieldSetElement
 * @param {Element | null} element - The element to check
 * @returns {element is HTMLFieldSetElement}
 */
function isHTMLFieldSetElement(element) {
  return element !== null && element instanceof HTMLFieldSetElement;
}

// ==================== LocalStorage Persistence ====================

/**
 * @typedef {object} ExamState
 * @property {string} type - The exam type (choice, categorization, hotspot, etc.)
 * @property {number[]} hintsUsed - Array of hint indices that have been revealed
 * @property {number | null} timeRemaining - Remaining time in seconds (null if no timer)
 * @property {string[] | undefined} selectedAnswers - For choice/truefalse: array of selected answer values
 * @property {Record<string, string | null> | undefined} categorizationState - For categorization: item index -> category index mapping
 * @property {string[] | undefined} hotspotClicked - For hotspot: array of clicked region indices
 * @property {string[] | undefined} orderingOrder - For ordering: array of item indices in current order
 * @property {string | undefined} numericValue - For numeric: the entered number value
 * @property {string[] | undefined} codeBlankValues - For code-completion: array of blank input values
 * @property {string[] | undefined} matchingSelections - For matching: array of dropdown selection values
 * @property {string[] | undefined} textInputValues - For text/essay: array of text input values
 */

/**
 * @typedef {object} StoredExamData
 * @property {number} timestamp - Unix timestamp when state was saved
 * @property {ExamState} state - The exam state object
 */

/** @type {string} - Prefix for localStorage keys */
const STORAGE_PREFIX = "mkdocs-exam-state:";

/** @type {number} - Hours before saved state expires */
const EXPIRY_HOURS = 24;

/**
 * Generate unique storage key for an exam based on page path and exam index
 * @param {number} examIndex - Zero-based index of exam on the page
 * @returns {string} Unique storage key
 */
function getStorageKey(examIndex) {
  const path = window.location.pathname;
  return `${STORAGE_PREFIX}${path}:exam-${examIndex}`;
}

/**
 * Save exam state to localStorage with timestamp
 * @param {number} examIndex - Zero-based index of exam on the page
 * @param {ExamState} state - The exam state to save
 * @returns {void}
 */
function saveExamState(examIndex, state) {
  try {
    /** @type {StoredExamData} */
    const data = {
      timestamp: Date.now(),
      state,
    };
    localStorage.setItem(getStorageKey(examIndex), JSON.stringify(data));
  } catch (e) {
    console.warn("Failed to save exam state:", e);
  }
}

/**
 * Load exam state from localStorage
 * @param {number} examIndex - Zero-based index of exam on the page
 * @returns {ExamState|null} Saved exam state, or null if expired/not found
 */
function loadExamState(examIndex) {
  try {
    const key = getStorageKey(examIndex);
    const json = localStorage.getItem(key);
    if (!json) return null;

    /** @type {StoredExamData} */
    const data = JSON.parse(json);
    const age = Date.now() - data.timestamp;
    const maxAge = EXPIRY_HOURS * 60 * 60 * 1000;

    if (age > maxAge) {
      localStorage.removeItem(key);
      return null;
    }

    return data.state;
  } catch (e) {
    console.warn("Failed to load exam state:", e);
    return null;
  }
}

/**
 * Clear exam state from localStorage
 * @param {number} examIndex - Zero-based index of exam on the page
 * @returns {void}
 */
function clearExamState(examIndex) {
  try {
    localStorage.removeItem(getStorageKey(examIndex));
  } catch (e) {
    console.warn("Failed to clear exam state:", e);
  }
}

// ==================== Initialize Exams ====================

// Initialize all exams on the page
document.querySelectorAll(".exam").forEach((exam, examIndex) => {
  // Ensure exam is an HTMLElement
  if (!isHTMLElement(exam)) {
    console.warn("Exam element is not an HTMLElement:", exam);
    return;
  }

  // Get form and fieldset with null checks
  const form = exam.querySelector("form");
  if (!form) {
    console.warn("Exam form not found for exam:", exam);
    return;
  }

  const fieldset = form.querySelector("fieldset");
  if (!fieldset) {
    console.warn("Exam fieldset not found for exam:", exam);
    return;
  }

  // Safely access exam data attributes
  const type = exam.dataset.type || "choice";
  const points = parseInt(exam.dataset.points || "1", 10) || 1;
  const timeLimit = exam.dataset.timeLimit
    ? parseInt(exam.dataset.timeLimit, 10)
    : undefined;

  let currentScore = points;
  /** @type {ReturnType<typeof setInterval> | null} */
  let timerInterval = null;
  let hintsUsed = 0;

  // Load saved state
  const savedState = loadExamState(examIndex);

  // Initialize hints
  const hintsContainer = exam.querySelector(".exam-hints");
  if (hintsContainer && isHTMLElement(hintsContainer)) {
    hintsContainer.classList.remove("hidden");
    const hintButtons = hintsContainer.querySelectorAll(".hint-button");

    // Restore hint state
    if (savedState && savedState.hintsUsed) {
      savedState.hintsUsed.forEach((hintIndex) => {
        const btn = hintButtons[hintIndex];
        if (btn && isHTMLButtonElement(btn)) {
          const hint = btn.parentElement;
          if (!hint || !isHTMLElement(hint)) return;

          const hintText = hint.querySelector(".hint-text");
          if (!hintText || !isHTMLElement(hintText)) return;

          const penalty = hint.dataset.penalty
            ? parseInt(hint.dataset.penalty, 10)
            : 0;

          hintText.classList.remove("hidden");
          currentScore = Math.max(0, currentScore - (points * penalty) / 100);
          hintsUsed++;
          btn.disabled = true;
          btn.textContent = `Hint ${hintIndex + 1} (used)`;
        }
      });
    }

    hintButtons.forEach((btn, index) => {
      if (!isHTMLButtonElement(btn)) return;

      btn.addEventListener("click", () => {
        const hint = btn.parentElement;
        if (!hint || !isHTMLElement(hint)) return;

        const hintText = hint.querySelector(".hint-text");
        if (!hintText || !isHTMLElement(hintText)) return;

        const penalty = hint.dataset.penalty
          ? parseInt(hint.dataset.penalty, 10)
          : 0;

        if (hintText.classList.contains("hidden")) {
          hintText.classList.remove("hidden");
          currentScore = Math.max(0, currentScore - (points * penalty) / 100);
          hintsUsed++;
          btn.disabled = true;
          btn.textContent = `Hint ${index + 1} (used)`;

          // Save hint usage
          saveExamState(examIndex, getCurrentState());
        }
      });
    });
  }

  // Initialize time limit
  if (timeLimit !== undefined && timeLimit > 0) {
    // Restore time remaining or use full time limit
    let timeRemaining =
      savedState && savedState.timeRemaining
        ? savedState.timeRemaining
        : timeLimit;
    const timerDiv = document.createElement("div");
    timerDiv.className = "exam-timer";
    timerDiv.textContent = `Time: ${timeRemaining}s`;
    exam.insertBefore(timerDiv, form);

    timerInterval = setInterval(() => {
      timeRemaining--;
      timerDiv.textContent = `Time: ${timeRemaining}s`;
      if (timeRemaining <= 10) {
        timerDiv.classList.add("warning");
      }
      if (timeRemaining <= 0) {
        if (timerInterval !== null) {
          clearInterval(timerInterval);
        }
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn && isHTMLButtonElement(submitBtn)) {
          submitBtn.click();
          submitBtn.disabled = true;
        }
      }

      // Save time remaining every second
      saveExamState(examIndex, getCurrentState());
    }, 1000);
  }

  // Function to capture current exam state
  /**
   * @returns {ExamState}
   */
  function getCurrentState() {
    /** @type {ExamState} */
    const state = {
      type,
      hintsUsed: [],
      timeRemaining: null,
      selectedAnswers: undefined,
      categorizationState: undefined,
      hotspotClicked: undefined,
      orderingOrder: undefined,
      numericValue: undefined,
      codeBlankValues: undefined,
      matchingSelections: undefined,
      textInputValues: undefined,
    };

    // Capture hint state
    const hintContainer = exam.querySelector(".exam-hints");
    if (hintContainer && isHTMLElement(hintContainer)) {
      const hintButtons = hintContainer.querySelectorAll(".hint-button");
      hintButtons.forEach((btn, index) => {
        if (isHTMLButtonElement(btn) && btn.disabled) {
          state.hintsUsed.push(index);
        }
      });
    }

    // Capture time remaining (from closure)
    if (timerInterval !== null) {
      const timerDiv = exam.querySelector(".exam-timer");
      if (timerDiv && isHTMLElement(timerDiv) && timerDiv.textContent) {
        const match = timerDiv.textContent.match(/(\d+)s/);
        if (match && match[1]) {
          state.timeRemaining = parseInt(match[1], 10);
        }
      }
    }

    // Null checks for form and fieldset
    if (!form || !fieldset) {
      return state;
    }

    // Capture type-specific state
    if (type === "choice" || type === "truefalse") {
      const selected = form.querySelectorAll('input[name="answer"]:checked');
      state.selectedAnswers = Array.from(selected).map((input) => {
        if (isHTMLInputElement(input)) {
          return input.value;
        }
        return "";
      });
    } else if (type === "categorization") {
      /** @type {Record<string, string | null>} */
      const categorizationState = {};
      const container = fieldset.querySelector(".categorization-container");
      if (container && isHTMLElement(container)) {
        const items = container.querySelectorAll(".categorization-item");
        items.forEach((item) => {
          if (!isHTMLElement(item)) return;
          const itemIndex = item.dataset.itemIndex;
          if (!itemIndex) return;
          const currentParent = item.closest(".categorization-category");
          const categoryIndex =
            currentParent && isHTMLElement(currentParent)
              ? currentParent.dataset.categoryIndex
              : null;
          categorizationState[itemIndex] = categoryIndex || null;
        });
      }
      state.categorizationState = categorizationState;
    } else if (type === "hotspot") {
      const clickedRegions = fieldset.querySelectorAll(
        ".hotspot-region.clicked",
      );
      state.hotspotClicked = Array.from(clickedRegions).map((r) => {
        if (isHTMLElement(r)) {
          return r.dataset.regionIndex || "";
        }
        return "";
      });
    } else if (type === "ordering") {
      const container = fieldset.querySelector(".ordering-container");
      if (container && isHTMLElement(container)) {
        const items = Array.from(container.querySelectorAll(".ordering-item"));
        state.orderingOrder = items.map((item) => {
          if (isHTMLElement(item)) {
            return item.dataset.index || "";
          }
          return "";
        });
      }
    } else if (type === "numeric") {
      const input = fieldset.querySelector('input[type="number"]');
      if (input && isHTMLInputElement(input)) {
        state.numericValue = input.value;
      }
    } else if (type === "code-completion") {
      const inputs = fieldset.querySelectorAll("input.code-blank");
      state.codeBlankValues = Array.from(inputs).map((input) => {
        if (isHTMLInputElement(input)) {
          return input.value;
        }
        return "";
      });
    } else if (type === "matching") {
      const selects = fieldset.querySelectorAll('select[name="answer"]');
      state.matchingSelections = Array.from(selects).map((select) => {
        if (isHTMLSelectElement(select)) {
          return select.value;
        }
        return "";
      });
    } else {
      // short-answer, fill, essay
      const inputs = fieldset.querySelectorAll(
        'input[type="text"][name="answer"], textarea[name="answer"]',
      );
      state.textInputValues = Array.from(inputs).map((input) => {
        if (isHTMLInputElement(input) || input instanceof HTMLTextAreaElement) {
          return input.value;
        }
        return "";
      });
    }

    return state;
  }

  // Restore saved state for all exam types
  if (savedState) {
    // Restore choice/truefalse answers
    if (type === "choice" || type === "truefalse") {
      if (savedState.selectedAnswers) {
        savedState.selectedAnswers.forEach((value) => {
          const input = form.querySelector(
            `input[name="answer"][value="${value}"]`,
          );
          if (input && isHTMLInputElement(input)) {
            input.checked = true;
          }
        });
      }
    }
    // Restore categorization
    else if (type === "categorization" && savedState.categorizationState) {
      const container = fieldset.querySelector(".categorization-container");
      if (container && isHTMLElement(container)) {
        Object.keys(savedState.categorizationState).forEach((itemIndex) => {
          if (!savedState.categorizationState) return;
          const categoryIndex = savedState.categorizationState[itemIndex];
          const item = container.querySelector(
            `.categorization-item[data-item-index="${itemIndex}"]`,
          );
          const category = container.querySelector(
            `.categorization-category[data-category-index="${categoryIndex}"]`,
          );
          if (
            item &&
            isHTMLElement(item) &&
            category &&
            isHTMLElement(category)
          ) {
            const dropZone = category.querySelector(".category-drop-zone");
            if (dropZone && isHTMLElement(dropZone)) {
              dropZone.appendChild(item);
            }
          }
        });
      }
    }
    // Restore hotspot
    else if (type === "hotspot" && savedState.hotspotClicked) {
      savedState.hotspotClicked.forEach((regionIndex) => {
        const region = fieldset.querySelector(
          `.hotspot-region[data-region-index="${regionIndex}"]`,
        );
        if (region && isHTMLElement(region)) {
          region.classList.add("clicked");
          if (region.hasAttribute("correct")) {
            region.classList.add("correct");
          } else {
            region.classList.add("wrong");
          }
        }
      });
    }
    // Restore ordering
    else if (type === "ordering" && savedState.orderingOrder) {
      const container = fieldset.querySelector(".ordering-container");
      if (container && isHTMLElement(container)) {
        /** @type {Record<string, HTMLElement>} */
        const itemsMap = {};
        container.querySelectorAll(".ordering-item").forEach((item) => {
          if (!isHTMLElement(item)) return;
          const index = item.dataset.index;
          if (index) {
            itemsMap[index] = item;
          }
        });
        container.innerHTML = "";
        savedState.orderingOrder.forEach((index) => {
          if (itemsMap[index]) {
            container.appendChild(itemsMap[index]);
          }
        });
      }
    }
    // Restore numeric
    else if (type === "numeric" && savedState.numericValue !== undefined) {
      const input = fieldset.querySelector('input[type="number"]');
      if (input && isHTMLInputElement(input)) {
        input.value = savedState.numericValue;
      }
    }
    // Restore code-completion
    else if (type === "code-completion" && savedState.codeBlankValues) {
      const inputs = fieldset.querySelectorAll("input.code-blank");
      savedState.codeBlankValues.forEach((value, index) => {
        const input = inputs[index];
        if (input && isHTMLInputElement(input)) {
          input.value = value;
        }
      });
    }
    // Restore matching
    else if (type === "matching" && savedState.matchingSelections) {
      const selects = fieldset.querySelectorAll('select[name="answer"]');
      savedState.matchingSelections.forEach((value, index) => {
        const select = selects[index];
        if (select && isHTMLSelectElement(select)) {
          select.value = value;
        }
      });
    }
    // Restore text inputs
    else if (savedState.textInputValues) {
      const inputs = fieldset.querySelectorAll(
        'input[type="text"][name="answer"], textarea[name="answer"]',
      );
      savedState.textInputValues.forEach((value, index) => {
        const input = inputs[index];
        if (
          input &&
          (isHTMLInputElement(input) || input instanceof HTMLTextAreaElement)
        ) {
          input.value = value;
        }
      });
    }
  }

  // Store save function on exam element for use in drag handlers
  exam._saveState = () => saveExamState(examIndex, getCurrentState());

  // Add event listeners to save state on input changes
  form.querySelectorAll("input, textarea, select").forEach((input) => {
    input.addEventListener("change", () => {
      if (exam._saveState) {
        exam._saveState();
      }
    });
    input.addEventListener("input", () => {
      if (exam._saveState) {
        exam._saveState();
      }
    });
  });

  // Handle form submission
  form.addEventListener("submit", (event) => {
    event.preventDefault();

    if (timerInterval !== null) {
      clearInterval(timerInterval);
    }

    let isCorrect = false;

    if (type === "choice" || type === "truefalse") {
      const selected = form.querySelectorAll('input[name="answer"]:checked');
      const correct = fieldset.querySelectorAll(
        'input[name="answer"][correct]',
      );
      isCorrect = selected.length === correct.length;
      for (let i = 0; i < selected.length; i++) {
        const input = selected[i];
        if (input && !input.hasAttribute("correct")) {
          isCorrect = false;
          break;
        }
      }
      // Convert NodeListOf<Element> to array of HTMLInputElement
      /** @type {HTMLInputElement[]} */
      const selectedInputs = Array.from(selected).filter(isHTMLInputElement);
      if (selectedInputs.length > 0) {
        markFields(selectedInputs, isCorrect);
        // Show answer feedback
        showAnswerFeedback(selectedInputs);
      }
    } else if (type === "matching") {
      const selects = fieldset.querySelectorAll('select[name="answer"]');
      isCorrect = true;
      selects.forEach((sel) => {
        if (!isHTMLSelectElement(sel)) return;
        const expected = sel.getAttribute("correct");
        const ok = sel.value === expected;
        if (!ok) {
          isCorrect = false;
        }
        sel.classList.add(ok ? "correct" : "wrong");
      });
    } else if (type === "numeric") {
      const input = fieldset.querySelector('input[type="number"]');
      if (input && isHTMLInputElement(input)) {
        const correctAttr = input.dataset.correct;
        const toleranceAttr = input.dataset.tolerance;
        const userValue = parseFloat(input.value);
        const correctValue = correctAttr ? parseFloat(correctAttr) : 0;
        const tolerance = toleranceAttr ? parseFloat(toleranceAttr) : 0.01;
        isCorrect = Math.abs(userValue - correctValue) <= tolerance;
        input.classList.add(isCorrect ? "correct" : "wrong");
      }
    } else if (type === "code-completion") {
      const inputs = fieldset.querySelectorAll("input.code-blank");
      isCorrect = true;
      inputs.forEach((input) => {
        if (!isHTMLInputElement(input)) return;
        const expected = (input.getAttribute("correct") || "").split("|");
        const val = input.value.trim();
        const ok = expected.map((e) => e.trim()).includes(val);
        if (!ok) {
          isCorrect = false;
        }
        input.classList.add(ok ? "correct" : "wrong");
      });
    } else if (type === "ordering") {
      const container = fieldset.querySelector(".ordering-container");
      if (container && isHTMLElement(container)) {
        const items = Array.from(container.querySelectorAll(".ordering-item"));
        const userOrder = items.map((item) => {
          if (isHTMLElement(item) && item.dataset.index) {
            return parseInt(item.dataset.index, 10);
          }
          return 0;
        });
        const correctOrderAttr = container.dataset.correctOrder;
        if (correctOrderAttr) {
          const correctOrder = correctOrderAttr
            .split(",")
            .map((x) => parseInt(x, 10));
          isCorrect =
            JSON.stringify(userOrder) === JSON.stringify(correctOrder);
        }
        container.classList.add(isCorrect ? "correct" : "wrong");
      }
    } else if (type === "categorization") {
      const container = fieldset.querySelector(".categorization-container");
      if (container && isHTMLElement(container)) {
        const items = container.querySelectorAll(".categorization-item");
        isCorrect = true;
        items.forEach((item) => {
          if (!isHTMLElement(item)) return;
          const correctCat = item.dataset.correctCategory;
          const currentParent = item.closest(".categorization-category");
          const currentCat =
            currentParent && isHTMLElement(currentParent)
              ? currentParent.dataset.categoryIndex
              : null;
          if (correctCat !== currentCat) {
            isCorrect = false;
          }
        });
        container.classList.add(isCorrect ? "correct" : "wrong");
      }
    } else if (type === "hotspot") {
      const clickedRegions = fieldset.querySelectorAll(
        ".hotspot-region.clicked",
      );
      const correctRegions = fieldset.querySelectorAll(
        ".hotspot-region[correct]",
      );
      isCorrect = clickedRegions.length === correctRegions.length;
      correctRegions.forEach((region) => {
        if (!region.classList.contains("clicked")) {
          isCorrect = false;
        }
      });
      clickedRegions.forEach((region) => {
        if (!region.hasAttribute("correct")) {
          isCorrect = false;
        }
      });
    } else {
      // short-answer, fill, essay
      const inputs = fieldset.querySelectorAll(
        'input[type="text"][name="answer"], textarea[name="answer"]',
      );
      resetFieldset(fieldset);
      isCorrect = true;
      for (let i = 0; i < inputs.length; i++) {
        const input = inputs[i];
        if (!input) continue;
        const expected = (input.getAttribute("correct") || "").split("|");
        let val = "";
        if (isHTMLInputElement(input) || input instanceof HTMLTextAreaElement) {
          val = input.value.trim().toLowerCase();
        }
        const ok = expected.map((e) => e.trim().toLowerCase()).includes(val);
        if (!ok) {
          isCorrect = false;
        }
        input.classList.add(ok ? "correct" : "wrong");
      }
    }

    // Show/hide content based on correctness
    const section = exam.querySelector("section.content");
    if (section && isHTMLElement(section)) {
      if (isCorrect) {
        section.classList.remove("hidden");
      } else {
        section.classList.add("hidden");
      }
    }

    // Show explanation based on setting
    const explanation = exam.querySelector(".exam-explanation");
    if (explanation && isHTMLElement(explanation)) {
      const showWhen = explanation.dataset.show || "on-correct";
      if (
        showWhen === "always" ||
        (showWhen === "on-correct" && isCorrect) ||
        (showWhen === "on-wrong" && !isCorrect)
      ) {
        explanation.classList.remove("hidden");
      }
    }

    // Show score
    const scoreDiv = document.createElement("div");
    scoreDiv.className = "exam-score";
    scoreDiv.textContent = isCorrect
      ? `✓ Correct! Score: ${currentScore}/${points} points`
      : "✗ Incorrect. Try again!";

    const existingScore = exam.querySelector(".exam-score");
    if (existingScore) {
      existingScore.replaceWith(scoreDiv);
    } else {
      form.appendChild(scoreDiv);
    }

    // Disable submit button
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn && isHTMLButtonElement(submitBtn)) {
      submitBtn.disabled = true;
    }

    // Clear saved state on successful submit
    clearExamState(examIndex);
  });
});

/**
 * Mark selected answer fields as correct or wrong
 * @param {HTMLInputElement[]} selected - Selected input elements
 * @param {boolean} _correct - Whether the overall answer is correct (unused, kept for compatibility)
 * @returns {void}
 */
function markFields(selected, _correct) {
  if (selected.length === 0) return;
  const firstInput = selected[0];
  if (!firstInput) return;
  const fieldset = firstInput.closest("fieldset");
  if (fieldset && isHTMLFieldSetElement(fieldset)) {
    resetFieldset(fieldset);
  }
  for (let i = 0; i < selected.length; i++) {
    const input = selected[i];
    if (!input) continue;
    const parent = input.parentElement;
    if (!parent) continue;
    if (!input.hasAttribute("correct")) {
      parent.classList.add("wrong");
    } else {
      parent.classList.add("correct");
    }
  }
}

/**
 * Reset fieldset by removing correct/wrong classes from all children
 * @param {HTMLFieldSetElement} fieldset - The fieldset element to reset
 * @returns {void}
 */
function resetFieldset(fieldset) {
  const fieldsetChildren = fieldset.children;
  for (let i = 0; i < fieldsetChildren.length; i++) {
    const child = fieldsetChildren[i];
    if (!child) continue;
    child.classList.remove("wrong");
    child.classList.remove("correct");
    const input = child.querySelector("input, textarea, select");
    if (input) {
      input.classList.remove("wrong");
      input.classList.remove("correct");
    }
  }
}

/**
 * Show feedback messages for selected answer inputs
 * @param {HTMLInputElement[]} selectedInputs - Selected input elements with feedback
 * @returns {void}
 */
function showAnswerFeedback(selectedInputs) {
  selectedInputs.forEach((input) => {
    const feedback = input.dataset.feedback;
    if (feedback) {
      const feedbackDiv = document.createElement("div");
      feedbackDiv.className = "answer-feedback";
      feedbackDiv.textContent = feedback;
      const parent = input.parentElement;
      if (parent) {
        parent.appendChild(feedbackDiv);
      }
    }
  });
}

// Add drag-and-drop support for ordering questions
document.querySelectorAll(".ordering-container").forEach((container) => {
  if (!isHTMLElement(container)) return;

  /** @type {HTMLElement | null} */
  let draggedItem = null;

  // Find exam element for state persistence
  const examElement = container.closest(".exam");
  if (!examElement || !isHTMLElement(examElement)) return;

  container.querySelectorAll(".ordering-item").forEach((item) => {
    if (!isHTMLElement(item)) return;
    item.draggable = true;

    item.addEventListener("dragstart", () => {
      draggedItem = item;
      item.classList.add("dragging");
    });

    item.addEventListener("dragend", () => {
      item.classList.remove("dragging");
      // Save state after drag ends
      if (examElement._saveState) {
        examElement._saveState();
      }
    });

    item.addEventListener("dragover", (e) => {
      e.preventDefault();
    });

    item.addEventListener("drop", (e) => {
      e.preventDefault();
      if (draggedItem && draggedItem !== item) {
        const allItems = Array.from(container.children);
        const draggedIndex = allItems.indexOf(draggedItem);
        const targetIndex = allItems.indexOf(item);

        const parent = item.parentNode;
        if (parent) {
          if (draggedIndex < targetIndex) {
            parent.insertBefore(draggedItem, item.nextSibling);
          } else {
            parent.insertBefore(draggedItem, item);
          }
        }
      }
    });
  });
});

// Add drag-and-drop support for categorization questions
document.querySelectorAll(".categorization-container").forEach((container) => {
  if (!isHTMLElement(container)) return;

  /** @type {HTMLElement | null} */
  let draggedItem = null;

  // Find exam element for state persistence
  const examElement = container.closest(".exam");
  if (!examElement || !isHTMLElement(examElement)) return;

  container.querySelectorAll(".categorization-item").forEach((item) => {
    if (!isHTMLElement(item)) return;
    item.draggable = true;

    item.addEventListener("dragstart", () => {
      draggedItem = item;
      item.classList.add("dragging");
    });

    item.addEventListener("dragend", () => {
      item.classList.remove("dragging");
      // Save state after drag ends
      if (examElement._saveState) {
        examElement._saveState();
      }
    });
  });

  container.querySelectorAll(".category-drop-zone").forEach((dropZone) => {
    if (!isHTMLElement(dropZone)) return;

    dropZone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropZone.classList.add("drag-over");
    });

    dropZone.addEventListener("dragleave", () => {
      dropZone.classList.remove("drag-over");
    });

    dropZone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropZone.classList.remove("drag-over");
      if (draggedItem) {
        dropZone.appendChild(draggedItem);
        // Save state after drop
        if (examElement._saveState) {
          examElement._saveState();
        }
      }
    });
  });
});

// Add click handling for hotspot questions
document.querySelectorAll(".hotspot-container").forEach((container) => {
  if (!isHTMLElement(container)) return;

  // Find exam element for state persistence
  const examElement = container.closest(".exam");
  if (!examElement || !isHTMLElement(examElement)) return;

  container.querySelectorAll(".hotspot-region").forEach((region) => {
    if (!isHTMLElement(region)) return;

    region.addEventListener("click", () => {
      region.classList.toggle("clicked");
      if (region.classList.contains("clicked")) {
        if (region.hasAttribute("correct")) {
          region.classList.add("correct");
        } else {
          region.classList.add("wrong");
        }
      } else {
        region.classList.remove("correct", "wrong");
      }

      // Save state after click
      if (examElement._saveState) {
        examElement._saveState();
      }
    });
  });
});

// Add partial credit calculation for choice questions
document.querySelectorAll('.exam[data-type="choice"]').forEach((exam) => {
  if (!isHTMLElement(exam)) return;
  const partialCredit = exam.dataset.partialCredit === "true";
  if (!partialCredit) return;

  const form = exam.querySelector("form");
  if (!form) return;

  form.addEventListener(
    "submit",
    () => {
      const selected = form.querySelectorAll('input[name="answer"]:checked');
      const correct = form.querySelectorAll('input[name="answer"][correct]');

      let earnedPoints = 0;
      let totalPoints = 0;

      // Calculate points based on weights
      correct.forEach((input) => {
        if (!isHTMLInputElement(input)) return;
        const weightAttr = input.dataset.weight;
        const weight = weightAttr ? parseFloat(weightAttr) : 1.0;
        totalPoints += weight;
      });

      selected.forEach((input) => {
        if (!isHTMLInputElement(input)) return;
        const weightAttr = input.dataset.weight;
        const weight = weightAttr ? parseFloat(weightAttr) : 1.0;
        if (input.hasAttribute("correct")) {
          earnedPoints += weight;
        } else {
          earnedPoints -= weight; // Penalty for incorrect selections
        }
      });

      // Normalize to 0-100%
      const percentage = Math.max(
        0,
        Math.min(100, (earnedPoints / totalPoints) * 100),
      );

      // Show partial credit score
      const scoreDiv = document.createElement("div");
      scoreDiv.className = "partial-credit-score";
      if (percentage === 100) {
        scoreDiv.className += " full";
      } else if (percentage >= 50) {
        scoreDiv.className += " partial";
      } else {
        scoreDiv.className += " zero";
      }
      scoreDiv.textContent = `Score: ${percentage.toFixed(0)}%`;
      form.appendChild(scoreDiv);
    },
    { once: true },
  );
});
