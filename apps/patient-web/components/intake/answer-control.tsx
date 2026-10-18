import type { IntakeQuestion } from "../../lib/intake/contracts";

type Props = {
  question: IntakeQuestion;
  disabled: boolean;
};

function numberConstraint(value: unknown): number | undefined {
  if (typeof value !== "string" && typeof value !== "number") return undefined;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : undefined;
}

export function AnswerControl({ question, disabled }: Props) {
  const describedBy = question.help_text ? "question-help" : undefined;
  const common = { disabled, "aria-describedby": describedBy };
  switch (question.answer_type) {
    case "TEXT":
      return (
        <textarea
          {...common}
          autoComplete="off"
          id="answer-value"
          maxLength={numberConstraint(question.constraints.max_length)}
          minLength={numberConstraint(question.constraints.min_length)}
          name="value"
          required={question.requiredness === "REQUIRED"}
          rows={5}
        />
      );
    case "SINGLE_CHOICE":
      return (
        <fieldset disabled={disabled}>
          <legend className="visually-hidden">{question.prompt}</legend>
          {question.options.map((option) => (
            <label className="choice-control" key={option.id}>
              <input name="selected_option_ids" required type="radio" value={option.id} />
              <span>{option.label}</span>
            </label>
          ))}
        </fieldset>
      );
    case "MULTI_CHOICE":
      return (
        <fieldset disabled={disabled}>
          <legend className="visually-hidden">{question.prompt}</legend>
          {question.options.map((option) => (
            <label className="choice-control" key={option.id}>
              <input name="selected_option_ids" type="checkbox" value={option.id} />
              <span>{option.label}</span>
            </label>
          ))}
        </fieldset>
      );
    case "BOOLEAN":
      return (
        <fieldset disabled={disabled}>
          <legend className="visually-hidden">{question.prompt}</legend>
          {[
            ["true", "Yes"],
            ["false", "No"],
          ].map(([value, label]) => (
            <label className="choice-control" key={value}>
              <input name="value" required type="radio" value={value} />
              <span>{label}</span>
            </label>
          ))}
        </fieldset>
      );
    case "NUMBER":
      return (
        <div className="answer-inline">
          <input
            {...common}
            id="answer-value"
            max={numberConstraint(question.constraints.maximum)}
            min={numberConstraint(question.constraints.minimum)}
            name="value"
            required
            step="any"
            type="number"
          />
          {typeof question.constraints.unit === "string" ? (
            <>
              <input name="unit" type="hidden" value={question.constraints.unit} />
              <span>{question.constraints.unit}</span>
            </>
          ) : null}
        </div>
      );
    case "DATE":
      return (
        <input
          {...common}
          id="answer-value"
          max={
            typeof question.constraints.latest === "string"
              ? question.constraints.latest
              : undefined
          }
          min={
            typeof question.constraints.earliest === "string"
              ? question.constraints.earliest
              : undefined
          }
          name="value"
          required
          type="date"
        />
      );
    case "DURATION":
      return (
        <div className="answer-inline">
          <input
            {...common}
            id="answer-value"
            min="0"
            name="value"
            required
            step="any"
            type="number"
          />
          <label>
            <span className="visually-hidden">Duration unit</span>
            <select disabled={disabled} name="unit" required>
              {Array.isArray(question.constraints.allowed_units)
                ? question.constraints.allowed_units.map((unit) => (
                    <option key={String(unit)} value={String(unit)}>
                      {String(unit)}
                    </option>
                  ))
                : null}
            </select>
          </label>
        </div>
      );
    case "SEVERITY_SCALE":
      return (
        <fieldset disabled={disabled}>
          <legend className="visually-hidden">Configured scale value</legend>
          <div className="scale-controls">
            {Array.isArray(question.constraints.allowed_values)
              ? question.constraints.allowed_values.map((value) => (
                  <label className="choice-control" key={String(value)}>
                    <input name="value" required type="radio" value={String(value)} />
                    <span>{String(value)}</span>
                  </label>
                ))
              : null}
          </div>
        </fieldset>
      );
  }
}
