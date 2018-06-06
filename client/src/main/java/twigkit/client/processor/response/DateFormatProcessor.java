package twigkit.client.processor.response;

import twigkit.model.Value;
import twigkit.search.processors.AbstractNamedFieldValueProcessor;

import java.text.SimpleDateFormat;
import java.util.Date;

/**
 * Format the display value of a date field.
 *
 * @author bjarkih
 */
public class DateFormatProcessor extends AbstractNamedFieldValueProcessor {

    private SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");

    @Override
    public Value processValue(Value value) {
        if (value.getActual() instanceof Date) {
            value.setDisplay(sdf.format((Date) value.getActual()));
        }
        return value;
    }
}


