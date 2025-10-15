import GLib from 'gi://GLib';

/**
 * Creates a debounced function that delays invoking the provided function
 * until after `wait` milliseconds have elapsed since the last time the
 * debounced function was invoked.
 *
 * @param {Function} func The function to debounce.
 * @param {number} wait The number of milliseconds to delay.
 * @returns {Function} Returns the new debounced function.
 */
export function createDebouncer(func, wait) {
    let timeoutId = 0;

    return function(...args) {
        // If there's an existing timeout, clear it.
        if (timeoutId > 0) {
            GLib.source_remove(timeoutId);
        }

        // Set a new timeout.
        timeoutId = GLib.timeout_add(GLib.PRIORITY_LOW, wait, () => {
            // When the timeout fires, execute the original function.
            func.apply(this, args);
            timeoutId = 0; // Clear the ID
            return GLib.SOURCE_REMOVE;
        });
    };
}