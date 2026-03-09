import { useEffect, useState } from "react";

export function useApiRequest(requestFactory, dependencies = []) {
  const [state, setState] = useState({
    data: null,
    error: null,
    isLoading: true,
  });
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    const abortController = new AbortController();

    setState({
      data: null,
      error: null,
      isLoading: true,
    });

    Promise.resolve(requestFactory({ signal: abortController.signal }))
      .then((data) => {
        if (!abortController.signal.aborted) {
          setState({
            data,
            error: null,
            isLoading: false,
          });
        }
      })
      .catch((error) => {
        if (!abortController.signal.aborted) {
          setState({
            data: null,
            error,
            isLoading: false,
          });
        }
      });

    return () => {
      abortController.abort();
    };
  }, [requestFactory, reloadToken, ...dependencies]);

  return {
    ...state,
    reload() {
      setReloadToken((value) => value + 1);
    },
  };
}
