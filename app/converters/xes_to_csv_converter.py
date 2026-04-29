import pandas as pd
import xml.etree.ElementTree as ET


class XesToCsvConverter:
    """Converter for transforming XES format into CSV logs."""

    xes_case_col = "case:concept:name"
    xes_activity_col = "concept:name"
    xes_timestamp_col = "time:timestamp"

    def convert(
        self,
        xes_tree: ET.ElementTree,
        include_all_attributes: bool,
    ) -> pd.DataFrame:
        """Convert a XES ElementTree to CSV dataframe.

        Parameters
        ----------
        xes_tree: ET.ElementTree
            The parsed XES XML tree.
        include_all_attributes: bool
            Whether to include all attributes in the CSV. If True, preserves original XES column names.
            If False, keeps only essential columns with user-friendly names.

        Returns
        -------
        pd.DataFrame
            The converted CSV dataframe.
        """
        df = self._parse_xes_to_dataframe(xes_tree)

        if df.empty:
            raise ValueError("The XES file contains no event data.")

        if include_all_attributes:
            return self._include_all_attributes(df)

        return self._keep_standard_columns(df)

    def _include_all_attributes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Include all attributes from XES file.

        Parameters
        ----------
        df : pd.DataFrame
            The parsed XES data.

        Returns
        -------
        pd.DataFrame
            Dataframe with standard XES columns.
        """
        standard_cols = [
            self.xes_case_col,
            self.xes_activity_col,
            self.xes_timestamp_col,
        ]
        existing_standard = [col for col in standard_cols if col in df.columns]
        other_cols = [col for col in df.columns if col not in standard_cols]
        return df[existing_standard + other_cols]

    def _keep_standard_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Keeping only standard three columns: id, event and timestamp.

        Parameters
        ----------
        df : pd.DataFrame
            The parsed XES data.

        Returns
        -------
        pd.DataFrame
            Dataframe containing only standard columns.

        Raises
        ------
        ValueError
            If there is no standard XES columns present.
        """
        standard_cols = [
            self.xes_case_col,
            self.xes_activity_col,
            self.xes_timestamp_col,
        ]
        existing_standard_cols = [col for col in standard_cols if col in df.columns]

        if not existing_standard_cols:
            raise ValueError("Could not find standard XES columns in the file.")

        df = df[existing_standard_cols]
        df = df.rename(
            columns={
                self.xes_case_col: "case_id",
                self.xes_activity_col: "activity",
                self.xes_timestamp_col: "timestamp",
            }
        )
        return df

    def _parse_xes_to_dataframe(self, xes_tree: ET.ElementTree) -> pd.DataFrame:
        """Parse an XES file and convert it to a pandas DataFrame.

        Parameters
        ----------
        xes_tree : ET.ElementTree
            XES XML tree.

        Returns
        -------
        pd.DataFrame
            The parsed XES data as a DataFrame.
        """
        root = xes_tree.getroot()

        ns: dict[str, str] = {}
        if root.tag.startswith("{"):
            ns_uri = root.tag[1 : root.tag.index("}")]
            ns = {"xes": ns_uri}

        events_data: list[dict[str, object]] = []

        traces = self._find_elements(root, "trace", ns)

        for trace in traces:
            trace_attrs = self._extract_attributes(trace, ns)
            case_id = trace_attrs.get("concept:name", str(id(trace)))

            events = self._find_elements(trace, "event", ns)

            for event in events:
                event_attrs = self._extract_attributes(event, ns)
                event_attrs["case:concept:name"] = case_id

                for key, value in trace_attrs.items():
                    if key != "concept:name":
                        event_attrs[f"case:{key}"] = value

                events_data.append(event_attrs)

        if not events_data:
            return pd.DataFrame()

        df = pd.DataFrame(events_data)

        if "time:timestamp" in df.columns:
            df["time:timestamp"] = pd.to_datetime(df["time:timestamp"], utc=True)

        return df

    def _extract_attributes(self, element: ET.Element, ns: dict) -> dict[str, object]:
        """Extract attributes from an XES element.

        Parameters
        ----------
        element : ET.Element
            The XML element from which attributes are extracted.
        ns : dict
            Namespace dictionary used for XES parsing.

        Returns
        -------
        dict[str, object]
            Dictionary of attribute key-value pairs.
        """
        attributes: dict[str, object] = {}
        attribute_types = ["string", "date", "int", "float", "boolean"]

        for attribute_type in attribute_types:
            # Search direct children only, not descendants
            elements = self._find_elements(element, attribute_type, ns, False)

            for attribute_elem in elements:
                key = attribute_elem.get("key", "")
                value = attribute_elem.get("value", "")

                if not key:
                    continue

                if attribute_type == "int":
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        pass
                elif attribute_type == "float":
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        pass
                elif attribute_type == "boolean":
                    value = value.lower() == "true"
                elif attribute_type == "date":
                    try:
                        value = pd.to_datetime(value)
                    except (ValueError, TypeError):
                        pass

                attributes[key] = value

        return attributes

    def _find_elements(
        self,
        element: ET.Element,
        tag: str,
        namespace: dict[str, str],
        descendants: bool = True,
    ) -> list[ET.Element]:
        """Find XML elements with optional namespace handling.

        Parameters
        ----------
        element : ET.Element
            XML element in which to search.
        tag : str
            Tag name to search for.
        namespace : dict[str, str]
            Namespace dictionary used for XES parsing.
        descendants : bool, optional
            Whether to search recursively through descendants, by default True.

        Returns
        -------
        list[ET.Element]
            List of matching XML elements.
        """
        path_prefix = ".//" if descendants else ""

        if namespace:
            matches = element.findall(f"{path_prefix}xes:{tag}", namespace)
            if matches:
                return matches

        return element.findall(f"{path_prefix}{tag}")
