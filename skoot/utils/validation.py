# -*- coding: utf-8 -*-
#
# Author: Taylor Smith <taylor.smith@alkaline-ml.com>

from __future__ import absolute_import

import pandas as pd
import numpy as np
import copy

from .iterables import is_iterable

__all__ = [
    'check_dataframe',
    'validate_multiple_cols',
    'validate_multiple_rows',
    'validate_test_set_columns'
]


def check_dataframe(X, cols=None, assert_all_finite=False, column_diff=False):
    """Check an input dataframe.

    Determine whether an input frame is a Pandas dataframe or whether it can
    be coerced as one, and raise a TypeError if not. Also check for finite
    values if specified. If columns are provided, checks that all columns
    are present within the dataframe and raises an assertion error if not.

    Note that if the input ``X`` is *not* a dataframe, and columns are
    provided via the ``cols`` arg, a ValueError will be raised.

    Parameters
    ----------
    X : array-like, shape=(n_samples, n_features)
        The input frame. If not a Pandas DataFrame, will raise a
        TypeError.

    cols : list, iterable or None
        Any columns to check for. If this is provided, all columns will
        be checked for presence in the ``X.columns`` index. If any are not
        present, a ValueError will be raised.

    assert_all_finite : bool, optional (default=False)
        Whether to assert that all values within the ``X`` frame are
        finite. Note that if ``cols`` is specified, this will only assert
        all values in the specified columns are finite.

    column_diff : bool, optional (default=False)
        Whether to also get the columns present in ``X`` that are not present
        in ``cols``. This is returned as the third element in the output if
        ``column_diff`` is True.

    Returns
    -------
    X_copy : pd.DataFrame
        A copy of the ``X`` dataframe.

    cols : list
        The list of columns on which to apply a function to this dataframe.
        if ``cols`` was specified in the function, this is equal to ``cols``
        as a list. Else, it's the ``X.columns`` index.

    diff : list
        If ``column_diff`` is True, will return as the third position in the
        tuple the columns that are within ``X`` but NOT present in ``cols``.
    """
    # determine if it's currently a DF or if it needs to be cast as one.
    if not isinstance(X, pd.DataFrame):
        if not is_iterable(X):
            raise TypeError("X must be a DataFrame, iterable or np.ndarray, "
                            "but got type=%s" % type(X))

        # if columns was defined, we have to break
        if cols is not None:
            raise ValueError("When X is not a DataFrame, cols cannot be "
                             "defined. Either pre-cast your data to Pandas, "
                             "or pass cols=None.")
        X = pd.DataFrame.from_records(X)

    # if columns are provided, check...
    present_columns = set(X.columns)
    if cols is not None:
        # ensure iterable, or copy if not
        cols = copy.deepcopy(cols) if is_iterable(cols) else [cols]

        # better to use "any" since it will short circuit!
        if any(c not in present_columns for c in cols):
            raise ValueError("All columns in `cols` must be present in X. "
                             "X columns=%r" % present_columns)

    # otherwise, if not specified, make sure we define it since we
    # end up returning cols (this is converted to a list in the next step)
    else:
        cols = X.columns

    # cols might have been a np.array or might be an Index -- make it a list
    if hasattr(cols, 'tolist'):
        cols = cols.tolist()

    # if specified, check that all values are finite
    if assert_all_finite and \
            X[cols].apply(lambda x: (~np.isfinite(x)).sum()).sum() > 0:
        raise ValueError('Expected all entries in specified columns '
                         'to be finite')

    # get the copy of X to return
    X_copy = X.copy()

    # if column diff is defined, we need to get it...
    if column_diff:
        colset = set(cols)
        diff = [c for c in present_columns if c not in colset]  # O(1) lookup
        return X_copy, cols, diff

    return X_copy, cols


def validate_multiple_cols(clsname, cols):
    """Validate that there are at least two columns to evaluate.

    This is used for various feature selection techniques, as well as
    in several feature extraction techniques.

    Parameters
    ----------
    clsname : str or unicode
        The name of the class that is calling the function.
        Used for more clear error messages.

    cols : array-like, shape=(n_features,)
        The columns to evaluate. If ``cols`` is not None
        and the length is less than 2, will raise a
        ``ValueError``.
    """
    if len(cols) < 2:
        raise ValueError('%s requires at least two features. Your data '
                         '(or the passed ``cols`` parameter) includes too '
                         'few features (%i)' % (clsname, len(cols)))


def validate_multiple_rows(clsname, frame):
    """Validate that there are at least two samples to evaluate.

    This is used for various feature transformation techniques, such as
    box-cox and yeo-johnson transformations.

    Parameters
    ----------
    clsname : str or unicode
        The name of the class that is calling the function.
        Used for more clear error messages.

    frame : array-like or pd.DataFrame, shape=(n_features, n_features)
        The samples to evaluate. If contains less than two samples,
        will raise a ValueError.
    """
    n_samples = frame.shape[0]
    if n_samples < 2:
        raise ValueError('%s requires at least two samples. Your data '
                         'includes too few samples (%i)'
                         % (clsname, n_samples))


def validate_test_set_columns(fit_columns, test_columns):
    """Validate that the test set columns will work.

    This function checks that the ``fit_columns`` are present in the
    ``test_columns`` set and raises a ValueError if not.

    Parameters
    ----------
    fit_columns : list
        The column names the estimator was fit on.

    test_columns : list
        The column names the test set contains.
    """
    present_cols = set(test_columns)  # O(1) lookup
    if not all(t in present_cols for t in fit_columns):
        raise ValueError("Not all fit columns present in test data! "
                         "(expected=%r, present=%r)"
                         % (fit_columns, test_columns))
